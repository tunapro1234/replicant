"""
Self-contained CLI test harness.

Brings up the local oTree server (its own Docker setup), lets you pick a game,
auto-detects how many agents that game needs, runs them fully in LLM mode, and
prints the answers directly.

Usage:
    python scripts/run_game.py                  # interactive: pick a game
    python scripts/run_game.py --game dictator  # skip the menu
    python scripts/run_game.py --game dictator --model google/gemma-4-31b-it
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from replicant import run_batch
from replicant.games import GAMES
from replicant.env import load_dotenv

load_dotenv()  # pick up OPEN_ROUTER_API_KEY from .env if not already exported

SERVER = "http://localhost:8000"
REST_KEY = "test-rest-key"
REPO = os.path.join(os.path.dirname(__file__), "..")


def _up(timeout=3):
    try:
        urllib.request.urlopen(SERVER, timeout=timeout)
        return True
    except Exception:
        return False


def ensure_server():
    """Start the local oTree container if it isn't already responding."""
    if _up():
        return
    print("oTree not responding — starting it (docker compose up -d --build)...")
    subprocess.run(["docker", "compose", "up", "-d", "--build"], cwd=REPO, check=True)
    for _ in range(60):
        if _up():
            print("oTree is up.\n")
            return
        time.sleep(2)
    sys.exit("oTree did not come up in time.")


def session_configs():
    """Ask oTree which games (session configs) exist, and their sizes."""
    req = urllib.request.Request(f"{SERVER}/api/session_configs",
                                 headers={"otree-rest-key": REST_KEY})
    return json.load(urllib.request.urlopen(req))


def pick_game(configs, chosen):
    names = [c["name"] for c in configs]
    if chosen:
        if chosen not in names:
            sys.exit(f"Unknown game '{chosen}'. Available: {names}")
        return next(c for c in configs if c["name"] == chosen)
    print("Available games:")
    for i, c in enumerate(configs, 1):
        print(f"  {i}. {c['name']:<20} ({c['num_demo_participants']} participant(s))")
    choice = input("\nPick a game [number]: ").strip()
    return configs[int(choice) - 1]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--game", help="session config name (skips the menu)")
    p.add_argument("--model", default="google/gemma-4-31b-it")
    args = p.parse_args()

    if not os.environ.get("OPEN_ROUTER_API_KEY"):
        sys.exit("Set OPEN_ROUTER_API_KEY")

    ensure_server()
    cfg = pick_game(session_configs(), args.game)

    # The game tells us how many agents it needs — no hardcoding.
    name = cfg["name"]
    n = cfg["num_demo_participants"]
    print(f"\nRunning '{name}' with {n} LLM agent(s) on {args.model}...\n")

    # api_key stays None -> openrouter reads OPEN_ROUTER_API_KEY from the env.
    results = run_batch(SERVER, name, n, [""] * n, args.model, rest_key=REST_KEY)

    for r in results:
        decisions = {k: v for entry in r.get("log", [])
                     if "answers" in entry for k, v in entry["answers"].items()}
        if decisions:
            print(f"  {r['agent']}: {decisions}")
        elif "error" in r:
            print(f"  {r['agent']}: ERROR — {r['error']}")
        else:
            print(f"  {r['agent']}: (no decision — e.g. a receiver role)")

    # If this game has a registered metric + human baseline, show the comparison.
    if name in GAMES:
        spec = GAMES[name]
        value = spec["extract"](results)
        if value is not None:
            b = spec["baseline"]
            print(f"\n  {spec['label']}: {value:.1f}")
            print(f"  human baseline: {b['value']}  ({b['source']})")


if __name__ == "__main__":
    main()
