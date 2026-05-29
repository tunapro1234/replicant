"""
Analyze a dictator-game experiment.

Reads the simulator's raw output (results/<dir>/data.csv, one row per
rep/agent/field), turns each dictator decision into an offer (offer = 100 -
kept), and compares each persona to the human baseline. Prints a table + ASCII
chart and — if matplotlib is installed — saves PNG plots.

This is the RESEARCHER's side: the human baseline lives HERE, not in the
simulator. Dictator-specific; copy & adapt for other games.

Usage:
    python scripts/analyze_dictator.py
    python scripts/analyze_dictator.py --dir results/dictator_demo
"""

import argparse
import csv
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from replicant.stats import summarize

# Human baseline — Engel (2011) meta-analysis. Lives in the analysis, not the tool.
HUMAN = 28.35
HUMAN_ZERO_PCT = 36.0


def load(data_csv):
    """Read raw decisions -> {persona: [offers]}. Offer = 100 - kept."""
    offers = defaultdict(list)
    with open(data_csv) as f:
        for row in csv.DictReader(f):
            if row.get("field") == "kept" and row.get("value"):
                offers[row["persona"]].append(100 - float(row["value"]))
    return offers


def ascii_bar(value, lo=0, hi=100, width=40):
    frac = 0 if hi == lo else max(0, min(1, (value - lo) / (hi - lo)))
    n = int(round(frac * width))
    return "█" * n + "·" * (width - n)


def print_table(offers):
    print(f"\n{'persona':<18}{'N':<4}{'mean':<7}{'95% CI':<16}"
          f"{'gave 0%':<9}{'gave 50%':<10}{'gap vs human':<12}")
    print("-" * 76)
    for persona, vals in offers.items():
        s = summarize(vals)
        n = s["n"]
        mean = s["mean"]
        ci = (f"[{s['ci95_low']:.1f}, {s['ci95_high']:.1f}]"
              if s.get("sd") is not None else "(no spread)")
        zero = 100 * sum(1 for v in vals if v == 0) / n
        fair = 100 * sum(1 for v in vals if v == 50) / n
        gap = mean - HUMAN
        print(f"{persona:<18}{n:<4}{mean:<7.1f}{ci:<16}"
              f"{zero:<9.0f}{fair:<10.0f}{gap:+.1f}")
    print(f"\nhuman baseline (Engel 2011): mean offer {HUMAN}%, "
          f"~{HUMAN_ZERO_PCT:.0f}% give zero")


def print_ascii_chart(offers):
    print("\nMean offer (0────────────────────────────────────100):")
    for persona, vals in offers.items():
        m = summarize(vals)["mean"]
        print(f"  {persona:<18}{ascii_bar(m)} {m:.0f}%")
    print(f"  {'HUMAN (Engel)':<18}{ascii_bar(HUMAN)} {HUMAN:.0f}%")


def save_plots(offers, out_dir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib not installed — skipping PNGs; "
              "`pip install matplotlib` to enable)")
        return

    plots_dir = os.path.join(out_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    personas = list(offers)

    # 1. Bar chart: mean offer +/- 95% CI, with human baseline line.
    fig, ax = plt.subplots(figsize=(8, 5))
    means, errs = [], []
    for p in personas:
        s = summarize(offers[p])
        means.append(s["mean"])
        errs.append(s.get("ci95_margin") or 0)
    ax.bar(personas, means, yerr=errs, capsize=5, color="#4c72b0")
    ax.axhline(HUMAN, ls="--", color="crimson",
               label=f"human (Engel 2011): {HUMAN}%")
    ax.set_ylabel("Mean offer (% of pie given)")
    ax.set_title("Dictator game: mean offer by persona")
    ax.set_ylim(0, 100)
    ax.legend()
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    bar_path = os.path.join(plots_dir, "offers_bar.png")
    fig.savefig(bar_path, dpi=120)
    plt.close(fig)

    # 2. Histogram: distribution of offers per persona (the bimodal question).
    fig, ax = plt.subplots(figsize=(8, 5))
    bins = range(0, 105, 5)
    for p in personas:
        ax.hist(offers[p], bins=bins, alpha=0.5, label=p)
    ax.axvline(HUMAN, ls="--", color="crimson", label=f"human mean {HUMAN}%")
    ax.set_xlabel("Offer (% of pie given)")
    ax.set_ylabel("Count (reps)")
    ax.set_title("Dictator game: offer distribution by persona")
    ax.legend()
    plt.tight_layout()
    hist_path = os.path.join(plots_dir, "offers_hist.png")
    fig.savefig(hist_path, dpi=120)
    plt.close(fig)

    print(f"\nSaved plots:\n  {bar_path}\n  {hist_path}")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dir", default="results/dictator_demo",
                   help="experiment results dir (containing data.csv)")
    args = p.parse_args()

    data_csv = os.path.join(args.dir, "data.csv")
    if not os.path.exists(data_csv):
        sys.exit(f"No data.csv in {args.dir}. Run an experiment first.")

    offers = load(data_csv)
    if not offers:
        sys.exit(f"No dictator 'kept' decisions in {data_csv}.")
    print_table(offers)
    print_ascii_chart(offers)
    save_plots(offers, args.dir)


if __name__ == "__main__":
    main()
