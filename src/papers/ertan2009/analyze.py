"""
Ertan 2009 — analysis and paper comparison.
"""

from replicant import PaperComparison

from .config import REGIMES, PROFILES, PAPER_FINDINGS


def analyze(results: dict, label: str = "") -> dict:
    """
    Print summary statistics and compare to the original paper.

    Args:
        results: dict of {part_name: pandas.DataFrame} from BehavioralExperiment
        label: optional condition label for printing

    Returns:
        Summary dict with all key metrics.
    """
    prefix = f"[{label}] " if label else ""

    print(f"\n{'='*55}", flush=True)
    print(f"{prefix}RESULTS SUMMARY", flush=True)
    print(f"{'='*55}", flush=True)

    summary = {}

    # Baseline
    df_b = results["baseline"]
    contribs = df_b["answer.contribution"].astype(float)
    summary["baseline_mean"] = contribs.mean()
    summary["baseline_std"] = contribs.std()
    print(f"\nBaseline contribution: {contribs.mean():.1f} (SD={contribs.std():.1f})", flush=True)

    # Voting
    df_v = results["voting"]
    n = len(df_v)
    low_pct = (df_v["answer.vote_punish_low"] == "Yes").sum() / n
    high_pct = (df_v["answer.vote_punish_high"] == "Yes").sum() / n
    summary["vote_punish_low"] = low_pct
    summary["vote_punish_high"] = high_pct
    print(f"\nVoting:", flush=True)
    print(f"  Punish low:  {low_pct:.0%} ({int(low_pct*n)}/{n})", flush=True)
    print(f"  Punish high: {high_pct:.0%} ({int(high_pct*n)}/{n})", flush=True)

    # Regimes
    df_r = results["regimes"]
    print(f"\nContribution by regime:", flush=True)
    summary["regimes"] = {}
    for regime in REGIMES:
        vals = df_r[df_r["scenario.regime_name"] == regime]["answer.contribution"].astype(float)
        summary["regimes"][regime] = {"mean": vals.mean(), "std": vals.std()}
        print(f"  {regime:<20s}: {vals.mean():5.1f} (SD={vals.std():.1f})", flush=True)

    # Punishment
    df_p = results["punishment"]
    print(f"\nPunishment amount by profile:", flush=True)
    summary["punishment"] = {}
    for p in PROFILES:
        vals = df_p[df_p["scenario.profile_name"] == p["name"]]["answer.punish_amount"].astype(float)
        nonzero = (vals > 0).sum()
        summary["punishment"][p["name"]] = {
            "mean": vals.mean(), "std": vals.std(),
            "nonzero": int(nonzero), "n": len(vals),
        }
        print(
            f"  {p['name']:<20s}: {vals.mean():.2f} "
            f"(SD={vals.std():.2f}, punished={nonzero}/{len(vals)})",
            flush=True,
        )

    print(f"\nTarget distribution:", flush=True)
    targets = df_p["answer.punish_target"].value_counts()
    summary["targets"] = targets.to_dict()
    for target, count in targets.items():
        print(f"  {target:<30s}: {count:>3d} ({count/len(df_p)*100:.0f}%)", flush=True)

    # Paper comparison
    comp = PaperComparison("Ertan, Page & Putterman (2009)")
    for key, (val, desc) in PAPER_FINDINGS.items():
        comp.add_finding(key, val, desc)
    comp.compare("vote_punish_low_pct", low_pct)
    comp.compare("vote_punish_high_pct", high_pct)
    comp.report()

    return summary


def save_results(results: dict, prefix: str, output_dir: str = "results"):
    """Save raw DataFrames to CSV."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    for part_name, df in results.items():
        path = os.path.join(output_dir, f"{prefix}_{part_name}.csv")
        df.to_csv(path, index=False)
    print(f"Saved to {output_dir}/{prefix}_*.csv", flush=True)
