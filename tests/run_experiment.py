"""
End-to-end demo: the whole arc in one script.

    sampling.big5  --(specs)-->  personas.big5.personallm  --(prompts)-->
    runners.otree.run_batch  --(decisions)-->  compare to human baseline

Run a sampled Big Five population through the dictator game and compare the
mean offer to the human meta-analytic baseline (Engel 2011: 28.35%).

Usage:
    python tests/run_experiment.py
    python tests/run_experiment.py --n 6 --model google/gemma-4-31b-it
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from replicant.sampling import big5
from replicant.personas.big5 import personallm
from replicant.runners.otree import run_batch

SERVER = "http://localhost:8000"
REST_KEY = "test-rest-key"
HUMAN_DICTATOR_OFFER = 28.35  # Engel 2011 meta-analysis, mean offer %


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=6, help="number of agents")
    parser.add_argument("--model", default="google/gemma-4-31b-it")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if not os.environ.get("OPEN_ROUTER_API_KEY"):
        print("Set OPEN_ROUTER_API_KEY")
        sys.exit(1)

    # 1. SAMPLE a Big Five population
    specs = big5.sample(n=args.n, seed=args.seed)
    print(f"Sampled {args.n} Big Five specs:")
    for s in specs:
        print(f"  {s}")

    # 2. BUILD a persona per spec (big5 family: spec keys == build_prompt args)
    personas = [personallm(**s) for s in specs]

    # 3. RUN them through the dictator game on oTree
    print(f"\nRunning dictator on {args.model}...")
    results = run_batch(SERVER, "dictator", args.n, personas, args.model, REST_KEY)

    # 4. COMPARE offers to the human baseline
    offers = []
    for r in results:
        for entry in r.get("log", []):
            if "answers" in entry and "kept" in entry["answers"]:
                offers.append(100 - float(entry["answers"]["kept"]))

    print("\n" + "=" * 50)
    if offers:
        mean = sum(offers) / len(offers)
        print(f"Offers:        {offers}")
        print(f"Mean offer:    {mean:.1f}%")
        print(f"Human (Engel): {HUMAN_DICTATOR_OFFER}%")
    else:
        print("No offers extracted.")
    print("=" * 50)


if __name__ == "__main__":
    main()
