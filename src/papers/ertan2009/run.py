"""
Ertan 2009 — CLI entry point.

Usage:
    python -m papers.ertan2009.run -n 50
    python -m papers.ertan2009.run -n 50 --random-personalities
    python -m papers.ertan2009.run -n 20 --big5
"""

import os
import sys
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from replicant import PersonalityFactory

from .experiment import build
from .analyze import analyze, save_results


def main():
    parser = argparse.ArgumentParser(description="Ertan et al. 2009 replication")
    parser.add_argument("-n", type=int, default=50, help="Number of agents")
    parser.add_argument("--model", default="stepfun/step-3.5-flash")
    parser.add_argument("--big5", action="store_true",
                        help="Use BFI-2 named profiles (balanced)")
    parser.add_argument("--random-personalities", action="store_true",
                        help="Use random BFI-2 personalities sampled from population norms")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-prefix", default=None)
    args = parser.parse_args()

    exp = build(model=args.model)
    factory = PersonalityFactory()

    if args.big5:
        agents = factory.create_population(per_profile=max(1, args.n // 5))
        condition = "big5_profiles"
        print(f"BFI-2 profile agents: {len(agents)}", flush=True)
    elif args.random_personalities:
        agents = factory.create_random_population(n=args.n, seed=args.seed)
        condition = "big5_random"
        print(f"Random personality agents: {len(agents)} (seed={args.seed})", flush=True)
    else:
        agents = factory.create_default(n=args.n)
        condition = "default"

    prefix = args.output_prefix or condition

    results = exp.run(agents)
    summary = analyze(results, label=condition)
    save_results(results, prefix)

    summary_path = os.path.join("results", f"{prefix}_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Summary saved to {summary_path}", flush=True)


if __name__ == "__main__":
    main()
