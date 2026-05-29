"""
Theory-grounded mixture calibration — Horton, Filippas & Manning (2023),
"Homo Silicus", Section 2.2.1.

A single theory persona rarely matches humans, but a *mixture* of them can.
Represent each persona by its behavior (one number per game — e.g. the mean
dictator offer). Find mixture weights w on the simplex (w_i >= 0, sum w = 1)
minimizing the squared error between the weighted-average behavior and the
human target:

    minimize_w  || sum_i w_i * b_i  -  human_target ||^2

Horton calibrates over a *vector* of games (the 6 Charness-Rabin allocations),
which pins the weights down uniquely. This supports 1+ games; with one game and
two extreme personas (Gemma's self_interested->0, inequity_averse->50) the
mixture is identified by matching the mean.

Dependency-free: a coarse simplex grid search (fine for the handful of theory
personas in play). Horton used constrained least squares (scipy); the grid is
the transparent MVP equivalent.

Source: https://arxiv.org/abs/2301.07543 ; github.com/johnjosephhorton/homo_silicus
"""


def _as_vector(x):
    return [float(x)] if isinstance(x, (int, float)) else [float(v) for v in x]


def _simplex_grid(n, steps):
    """Integer compositions of `steps` into n non-negative parts."""
    if n == 1:
        yield (steps,)
        return
    for first in range(steps + 1):
        for rest in _simplex_grid(n - 1, steps - first):
            yield (first,) + rest


def fit_weights(behavior: dict, target, step: float = 0.01) -> tuple[dict, float]:
    """Fit mixture weights over personas to match a human target.

    Args:
        behavior: {persona: number or [numbers]} — each persona's behavior,
            one value per game (e.g. {"self_interested": 0, "inequity_averse": 50}).
        target: number or [numbers] — the human behavior to match (e.g. 28.35).
        step: simplex grid resolution (0.01 -> weights to the nearest 1%).

    Returns: ({persona: weight}, sse).
    """
    personas = list(behavior)
    vecs = {p: _as_vector(v) for p, v in behavior.items()}
    tgt = _as_vector(target)
    n, k = len(personas), len(tgt)
    steps = int(round(1 / step))

    best_w, best_sse = None, float("inf")
    for combo in _simplex_grid(n, steps):
        w = [c / steps for c in combo]
        pred = [sum(w[i] * vecs[personas[i]][j] for i in range(n)) for j in range(k)]
        sse = sum((pred[j] - tgt[j]) ** 2 for j in range(k))
        if sse < best_sse:
            best_sse, best_w = sse, w
    return {personas[i]: round(best_w[i], 4) for i in range(n)}, best_sse


def population(weights: dict, n: int) -> dict:
    """Turn mixture weights into integer agent counts for a population of n.

    Uses largest-remainder rounding so the counts sum to exactly n.
    Returns {persona: count}.
    """
    raw = {p: w * n for p, w in weights.items()}
    counts = {p: int(v) for p, v in raw.items()}
    short = n - sum(counts.values())
    # hand the leftover agents to the largest fractional remainders
    rema = sorted(raw, key=lambda p: raw[p] - counts[p], reverse=True)
    for p in rema[:short]:
        counts[p] += 1
    return counts
