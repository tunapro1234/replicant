"""
Big Five population sampler.

Produces {E, A, C, N, O} trait specs (each on the 1-5 BFI scale) by drawing
from population norms, then clipping to [1, 5]. The specs feed any persona in
personas/big5/ — that family's shared input contract is exactly these 5 keys.

Norms below are approximate US-adult values used as a starting population
model. Refine with exact published norms (e.g. Soto & John 2017, BFI-2 US
sample) when precision matters — the sampler interface stays the same.
"""

import random

# (mean, sd) per domain on the 1-5 scale. Approximate — see module docstring.
NORMS = {
    "E": (3.2, 0.9),
    "A": (3.7, 0.7),
    "C": (3.4, 0.7),
    "N": (2.9, 0.8),
    "O": (3.7, 0.7),
}

DOMAINS = ("E", "A", "C", "N", "O")


def sample(n: int = 1, seed: int = None, means: dict = None) -> list[dict]:
    """Sample n Big Five specs from population norms.

    Args:
        n: number of specs to draw.
        seed: RNG seed for reproducibility.
        means: optional per-domain mean overrides, e.g. {"A": 1.5} to model a
            disagreeable population. SD stays at the norm value.

    Returns:
        list of dicts like {"E": 3.41, "A": 2.88, "C": 3.6, "N": 2.7, "O": 3.9}
    """
    rng = random.Random(seed)
    means = means or {}
    specs = []
    for _ in range(n):
        spec = {}
        for d in DOMAINS:
            mean, sd = NORMS[d]
            mean = means.get(d, mean)
            val = rng.gauss(mean, sd)
            spec[d] = round(max(1.0, min(5.0, val)), 2)
        specs.append(spec)
    return specs
