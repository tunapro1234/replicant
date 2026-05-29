"""
MVP entry point — the whole arc in one script.

Builds a few persona "cells", runs each through the dictator game N times, and
reports mean +/- 95% CI vs the cited human baseline. Writes provenance + tidy
CSV + a methods sentence to results/<name>/.

    persona (theory or sampled big5)  -->  oTree dictator x reps  -->  stats vs human

Usage:
    python tests/run_experiment.py
    python tests/run_experiment.py --reps 5 --model google/gemma-4-31b-it
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from replicant.sampling import big5
from replicant.personas.big5 import personallm
from replicant.personas.economics.homo_silicus_2301_07543 import ALLOCATION_PERSONAS
from replicant.experiment import run_experiment
from replicant.report import summary_table
from replicant.env import load_dotenv

load_dotenv()  # pick up OPEN_ROUTER_API_KEY from .env if not already exported


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

    # Build the cells: (game, persona_string, label).
    # Two theory personas + one sampled-from-population Big Five persona.
    big5_spec = big5.sample(n=1, seed=args.seed)[0]
    cells_spec = [
        ("dictator", "", "baseline"),
        ("dictator", ALLOCATION_PERSONAS["self_interested"], "self_interested"),
        ("dictator", ALLOCATION_PERSONAS["inequity_averse"], "inequity_averse"),
        ("dictator", personallm(**big5_spec), "big5_sampled"),
    ]

    out = run_experiment("dictator_demo", cells_spec, args.model,
                         reps=args.reps, seed=args.seed, out_dir=args.out_dir)

    print(summary_table(out["cells"]))
    print(f"\nCost: ${out['cost_usd']:.4f}")
    print(f"Saved to {out['out_dir']}/ (results.json, data.csv, methods.txt)")


if __name__ == "__main__":
    main()
