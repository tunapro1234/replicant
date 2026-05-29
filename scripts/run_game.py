"""
Self-contained CLI test harness.

Brings up the local oTree server (its own Docker setup), lets you pick a game,
auto-detects how many agents that game needs, runs them fully in LLM mode, and
prints the answers directly.

Usage:
    python scripts/run_game.py                          # interactive: pick a game
    python scripts/run_game.py --game dictator          # one quick run, baseline
    python scripts/run_game.py --game dictator --persona self_interested
    python scripts/run_game.py --game dictator --persona self_interested --reps 10
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
from replicant.experiment import run_experiment
from replicant.report import summary_table
from replicant.personas.economics.homo_silicus_2301_07543 import (
    ALLOCATION_PERSONAS, POLITICAL_PERSONAS,
)
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


def resolve_persona(key):
    """Map a --persona key to (persona_string, label). 'baseline' = no persona."""
    if not key or key == "baseline":
        return "", "baseline"
    if key in ALLOCATION_PERSONAS:
        return ALLOCATION_PERSONAS[key], key
    if key in POLITICAL_PERSONAS:
        return POLITICAL_PERSONAS[key], key
    options = ["baseline"] + list(ALLOCATION_PERSONAS) + list(POLITICAL_PERSONAS)
    sys.exit(f"Unknown persona '{key}'. Options: {options}")


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
    p.add_argument("--persona", default="baseline",
                   help="baseline | self_interested | inequity_averse | efficient | "
                        "socialist | conservative | ...")
    p.add_argument("--reps", type=int, default=1,
                   help="repetitions; >1 gives mean +/- 95%% CI and saves results")
    p.add_argument("--model", default="google/gemma-4-31b-it")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    if not os.environ.get("OPEN_ROUTER_API_KEY"):
        sys.exit("Set OPEN_ROUTER_API_KEY")

    ensure_server()
    cfg = pick_game(session_configs(), args.game)
    name = cfg["name"]
    n = cfg["num_demo_participants"]
    persona, label = resolve_persona(args.persona)

    # Repeated, measured experiment: needs a registered metric + baseline.
    if args.reps > 1:
        if name not in GAMES:
            sys.exit(f"--reps needs a game with a registered metric. '{name}' has none "
                     f"(known: {list(GAMES)}). Use reps=1 for a raw run.")
        print(f"\n{name} | persona={label} | {args.reps} reps | {args.model}\n")
        out = run_experiment(f"{name}_{label}", [(name, persona, label)],
                             args.model, reps=args.reps, seed=args.seed,
                             out_dir="results")
        print(summary_table(out["cells"]))
        print(f"\nCost: ${out['cost_usd']:.4f}")
        print(f"Saved to {out['out_dir']}/")
        return

    # Single quick run.
    print(f"\nRunning '{name}' | persona={label} | {n} agent(s) | {args.model}...\n")
    results = run_batch(SERVER, name, n, [persona] * n, args.model, rest_key=REST_KEY)

    for r in results:
        decisions = {k: v for entry in r.get("log", [])
                     if "answers" in entry for k, v in entry["answers"].items()}
        if decisions:
            print(f"  {r['agent']}: {decisions}")
        elif "error" in r:
            print(f"  {r['agent']}: ERROR — {r['error']}")
        else:
            print(f"  {r['agent']}: (no decision — e.g. a receiver role)")

    if name in GAMES:
        spec = GAMES[name]
        value = spec["extract"](results)
        if value is not None:
            b = spec["baseline"]
            print(f"\n  {spec['label']}: {value:.1f}")
            print(f"  human baseline: {b['value']}  ({b['source']})")


if __name__ == "__main__":
    main()
