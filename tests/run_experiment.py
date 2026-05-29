"""
Demo entry point — run the dictator persona comparison and save raw data.

Builds a few persona "cells", runs each through the dictator game N times, and
saves the raw decisions + full transcripts to results/dictator_demo/. It does
NOT compute metrics or compare to humans — that's analysis:

    python scripts/analyze_dictator.py --dir results/dictator_demo

Usage:
    python tests/run_experiment.py
    python tests/run_experiment.py --reps 10 --model google/gemma-4-31b-it
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from replicant.sampling import big5
from replicant.personas.big5 import personallm
from replicant.personas.economics.homo_silicus_2301_07543 import ALLOCATION_PERSONAS
from replicant.experiment import run_experiment
from replicant.env import load_dotenv

load_dotenv()  # pick up OPEN_ROUTER_API_KEY from .env if not already exported

DICTATOR_N = 2  # oTree dictator pairs participants; one decides (num_demo_participants)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reps", type=int, default=5, help="repetitions per cell")
    parser.add_argument("--model", default="google/gemma-4-31b-it")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out-dir", default="results")
    args = parser.parse_args()

    if not os.environ.get("OPEN_ROUTER_API_KEY"):
        print("Set OPEN_ROUTER_API_KEY")
        sys.exit(1)

    # Cells: (game, persona_string, label). Theory personas + a sampled Big Five.
    big5_spec = big5.sample(n=1, seed=args.seed)[0]
    cells_spec = [
        ("dictator", "", "baseline"),
        ("dictator", ALLOCATION_PERSONAS["self_interested"], "self_interested"),
        ("dictator", ALLOCATION_PERSONAS["inequity_averse"], "inequity_averse"),
        ("dictator", personallm(**big5_spec), "big5_sampled"),
    ]

    out = run_experiment("dictator_demo", cells_spec, args.model, DICTATOR_N,
                         reps=args.reps, seed=args.seed, out_dir=args.out_dir)

    print(f"Ran {len(cells_spec)} personas x {args.reps} reps on dictator.")
    print(f"Cost: ${out['cost_usd']:.4f}")
    print(f"Saved raw data + transcripts to {out['out_dir']}/dictator_demo/")
    print("\nAnalyze it:\n  python scripts/analyze_dictator.py --dir "
          f"{out['out_dir']}/dictator_demo")


if __name__ == "__main__":
    main()
