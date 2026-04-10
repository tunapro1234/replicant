"""
TEMPLATE — analysis and paper comparison.

Implements analyze() and save_results() for this paper.
Customize the analyze() function to extract whatever metrics matter
for your specific paper.
"""

import os
from replicant import PaperComparison

from .config import PAPER_FINDINGS


def analyze(results: dict, label: str = "") -> dict:
    """
    Print summary statistics and compare to the original paper.

    Args:
        results: dict of {part_name: pandas.DataFrame} from BehavioralExperiment
        label: optional condition label for printing

    Returns:
        Summary dict with the metrics you care about.
    """
    prefix = f"[{label}] " if label else ""

    print(f"\n{'='*55}", flush=True)
    print(f"{prefix}RESULTS SUMMARY", flush=True)
    print(f"{'='*55}", flush=True)

    summary = {}

    # Example: extract a metric from your results
    # df = results["offer"]
    # avg_offer = df["answer.offer"].astype(float).mean()
    # summary["average_offer"] = avg_offer
    # print(f"Average offer: {avg_offer:.2f}", flush=True)

    # Compare to paper findings
    if PAPER_FINDINGS:
        comp = PaperComparison("Your Paper Citation")
        for key, (val, desc) in PAPER_FINDINGS.items():
            comp.add_finding(key, val, desc)
            if key in summary:
                comp.compare(key, summary[key])
        comp.report()

    return summary


def save_results(results: dict, prefix: str, output_dir: str = "results"):
    """Save raw DataFrames to CSV."""
    os.makedirs(output_dir, exist_ok=True)
    for part_name, df in results.items():
        path = os.path.join(output_dir, f"{prefix}_{part_name}.csv")
        df.to_csv(path, index=False)
    print(f"Saved to {output_dir}/{prefix}_*.csv", flush=True)
