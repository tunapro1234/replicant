"""
Summary statistics for repeated runs (DESIGN.md #3: N, not n=1).

Dependency-free. Uses a two-tailed 95% t-table so small-N confidence intervals
are honest (a normal-approx 1.96 understates the interval for, say, N=5).
"""

import math

# Two-tailed t critical values at 95% by degrees of freedom (n-1).
_T95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
    8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145,
    15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
    21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056,
    27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042,
}


def _t95(df: int) -> float:
    if df <= 0:
        return float("nan")
    if df in _T95:
        return _T95[df]
    return 1.96  # df > 30: normal approximation


def summarize(values: list[float]) -> dict:
    """Summary stats for a list of per-run metric values.

    Returns: {n, mean, sd, sem, ci95_margin, ci95_low, ci95_high}.
    For n < 2, dispersion fields are None (a single point has no spread).
    """
    vals = [v for v in values if v is not None]
    n = len(vals)
    if n == 0:
        return {"n": 0, "mean": None, "sd": None, "sem": None,
                "ci95_margin": None, "ci95_low": None, "ci95_high": None}

    mean = sum(vals) / n
    if n < 2:
        return {"n": n, "mean": mean, "sd": None, "sem": None,
                "ci95_margin": None, "ci95_low": mean, "ci95_high": mean}

    sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / (n - 1))
    sem = sd / math.sqrt(n)
    margin = _t95(n - 1) * sem
    return {
        "n": n, "mean": mean, "sd": sd, "sem": sem,
        "ci95_margin": margin,
        "ci95_low": mean - margin,
        "ci95_high": mean + margin,
    }
