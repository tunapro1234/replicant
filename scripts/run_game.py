"""
Self-contained CLI test harness.

Brings up the local oTree server (its own Docker setup), lets you pick a game,
auto-detects how many agents that game needs, runs them fully in LLM mode, and
prints the answers directly.

Usage:
    python scripts/run_game.py                          # interactive: pick a game
    python scripts/run_game.py --game dictator          # one quick run, baseline
    python scripts/run_game.py --game dictator --persona self_interested --reps 10
    python scripts/run_game.py --config config.yaml     # all params from a file
    python scripts/run_game.py --config config.yaml --reps 20   # flags override config
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
from replicant.experiment import run_experiment
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


def load_config(path):
    """Load a .yaml/.yml (needs pyyaml) or .json experiment config."""
    if path.endswith((".yaml", ".yml")):
        try:
            import yaml
        except ImportError:
            sys.exit("YAML config needs pyyaml: `pip install pyyaml` (or use a .json config).")
        with open(path) as f:
            return yaml.safe_load(f) or {}
    with open(path) as f:
        return json.load(f)


def resolve_persona(spec):
    """Map a persona spec to (persona_string, label).

    spec is either a name string (baseline / economic / political key) or a
    dict for a sampled persona, e.g. {type: big5, sampling: norms, seed: 42}.
    """
    if isinstance(spec, dict):
        if spec.get("type") == "big5":
            from replicant.sampling import big5
            from replicant.personas.big5 import personallm
            s = big5.sample(n=1, seed=spec.get("seed"))[0]
            return personallm(**s), "big5_sampled"
        sys.exit(f"Unknown persona spec: {spec}")
    if not spec or spec == "baseline":
        return "", "baseline"
    if spec in ALLOCATION_PERSONAS:
        return ALLOCATION_PERSONAS[spec], spec
    if spec in POLITICAL_PERSONAS:
        return POLITICAL_PERSONAS[spec], spec
    options = ["baseline"] + list(ALLOCATION_PERSONAS) + list(POLITICAL_PERSONAS)
    sys.exit(f"Unknown persona '{spec}'. Options: {options}")


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
    p.add_argument("--config", help="path to a .yaml/.json experiment config")
    # CLI flags default to None so they only override the config when set.
    p.add_argument("--game", default=None, help="session config name (skips the menu)")
    p.add_argument("--persona", default=None,
                   help="baseline | self_interested | inequity_averse | efficient | "
                        "socialist | conservative | ...")
    p.add_argument("--reps", type=int, default=None,
                   help="repetitions; >1 gives mean +/- 95%% CI and saves results")
    p.add_argument("--model", default=None)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--temperature", type=float, default=None)
    args = p.parse_args()

    if not os.environ.get("OPEN_ROUTER_API_KEY"):
        sys.exit("Set OPEN_ROUTER_API_KEY")

    # Merge: a CLI flag (if given) overrides the config, which overrides the default.
    # With no --config, auto-load config.yaml sitting next to this script.
    config_path = args.config
    if not config_path:
        default_cfg = os.path.join(os.path.dirname(__file__), "config.yaml")
        if os.path.exists(default_cfg):
            config_path = default_cfg
            print(f"(using {os.path.relpath(default_cfg)})")
    conf = load_config(config_path) if config_path else {}
    pick = lambda key, default: (getattr(args, key) if getattr(args, key) is not None
                                 else conf.get(key, default))
    game_name = pick("game", None)
    persona_spec = args.persona if args.persona is not None else conf.get("persona", "baseline")
    reps = pick("reps", 1)
    model = pick("model", "google/gemma-4-31b-it")
    seed = pick("seed", 42)
    temperature = pick("temperature", 1.0)

    ensure_server()
    cfg = pick_game(session_configs(), game_name)
    name = cfg["name"]
    n = cfg["num_demo_participants"]
    persona, label = resolve_persona(persona_spec)

    # Repeated run: save raw decisions + transcripts for later analysis.
    if reps > 1:
        print(f"\n{name} | persona={label} | {reps} reps | n={n} | "
              f"temp={temperature} | {model}\n")
        out = run_experiment(f"{name}_{label}", [(name, persona, label)],
                             model, n, reps=reps, seed=seed,
                             temperature=temperature, out_dir="results")
        print(f"Saved {reps} reps of raw decisions to {out['out_dir']}/")
        print(f"  results.json (full transcripts) + data.csv (raw decisions)")
        print(f"Cost: ${out['cost_usd']:.4f}")
        print(f"\nAnalyze it with your own script, e.g.:")
        print(f"  python scripts/analyze_dictator.py --dir {out['out_dir']}")
        return

    # Single quick run — print the raw decisions.
    print(f"\nRunning '{name}' | persona={label} | {n} agent(s) | {model}...\n")
    results = run_batch(SERVER, name, n, [persona] * n, model,
                        rest_key=REST_KEY, temperature=temperature, seed=seed)
    for r in results:
        decisions = {k: v for entry in r.get("log", [])
                     if "answers" in entry for k, v in entry["answers"].items()}
        if decisions:
            print(f"  {r['agent']}: {decisions}")
        elif "error" in r:
            print(f"  {r['agent']}: ERROR — {r['error']}")
        else:
            print(f"  {r['agent']}: (no decision — e.g. a receiver role)")


if __name__ == "__main__":
    main()
