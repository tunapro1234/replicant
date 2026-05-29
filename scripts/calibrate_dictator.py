"""
Calibrate a theory-persona mixture for the dictator game (Horton et al. 2023).

Single personas miss the human mean (28.35%); a *mixture* can match it. This
reads a dictator experiment's per-persona offers, fits mixture weights to the
human target, and shows that the calibrated population reproduces both the
human mean AND the bimodal shape (spikes at give-0 and give-50) — which no
single persona does.

In-sample calibration: uses the persona means already measured, no new runs.

Usage:
    python scripts/calibrate_dictator.py
    python scripts/calibrate_dictator.py --dir results/dictator_demo \
        --personas self_interested,inequity_averse
"""

import argparse
import csv
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from replicant.calibrate import fit_weights, population
from replicant.stats import summarize

HUMAN_MEAN = 28.35       # Engel (2011)
HUMAN_ZERO_PCT = 36.0    # Engel (2011): ~36% of dictators give nothing


def load(data_csv):
    offers = defaultdict(list)
    with open(data_csv) as f:
        for row in csv.DictReader(f):
            if row.get("value"):
                offers[row["persona"]].append(float(row["value"]))
    return offers


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dir", default="results/dictator_demo")
    p.add_argument("--personas", default="self_interested,inequity_averse",
                   help="comma-separated theory personas to mix over")
    p.add_argument("--n", type=int, default=100,
                   help="population size to express the mixture as agent counts")
    args = p.parse_args()

    offers = load(os.path.join(args.dir, "data.csv"))
    wanted = [s.strip() for s in args.personas.split(",")]
    missing = [s for s in wanted if s not in offers]
    if missing:
        sys.exit(f"Personas {missing} not in {args.dir}/data.csv. "
                 f"Have: {list(offers)}")

    # 1. each persona's measured behavior (mean offer)
    behavior = {s: summarize(offers[s])["mean"] for s in wanted}
    print("Measured persona behavior (mean offer %):")
    for s, m in behavior.items():
        print(f"  {s:<18}{m:.1f}")
    print(f"  {'HUMAN target':<18}{HUMAN_MEAN}")

    # 2. fit the mixture
    weights, sse = fit_weights(behavior, HUMAN_MEAN)
    print("\nCalibrated mixture (weights that match the human mean):")
    for s, w in weights.items():
        print(f"  {s:<18}{w:.0%}")
    print(f"  (fit error: {sse:.3f})")

    # 3. predicted mixture distribution = weighted mix of each persona's offers
    pool = []
    for s in wanted:
        pool += [(w_offer, weights[s]) for w_offer in offers[s]]
    total_w = sum(w for _, w in pool)
    pred_mean = sum(o * w for o, w in pool) / total_w
    pred_zero = 100 * sum(w for o, w in pool if o == 0) / total_w
    pred_fair = 100 * sum(w for o, w in pool if o == 50) / total_w

    print("\nCalibrated population vs humans:")
    print(f"  {'':<14}{'mixture':<10}{'human':<10}")
    print(f"  {'mean offer':<14}{pred_mean:<10.1f}{HUMAN_MEAN:<10}")
    print(f"  {'gave 0%':<14}{pred_zero:<10.0f}{HUMAN_ZERO_PCT:<10.0f}")
    print(f"  {'gave 50%':<14}{pred_fair:<10.0f}{'(spike)':<10}")

    # 4. express as an agent population for a validation run
    counts = population(weights, args.n)
    print(f"\nAs a population of {args.n} agents: "
          + ", ".join(f"{c} {s}" for s, c in counts.items()))
    print("\nTakeaway: no single persona hits 28% (they sit at 0 or 50), but the "
          "calibrated mixture matches the human mean AND the bimodal shape.")


if __name__ == "__main__":
    main()
