"""
Sampling layer — produces person-specs that tell the persona layer WHAT to build.

A sampler outputs specs (e.g. trait dicts) drawn from a population definition:
published norms, a CSV of real respondents, a joint demographic distribution.

Contract: sampling is upstream and dumb about everything below it. It never
knows how a spec becomes a prompt, and it never knows about calibration — that
is the persona layer's job. A spec flows one direction:

    sampling --(spec)--> persona --(prompt)--> runner --> provider

Sampling is per-family (a big5 sampler produces {E,A,C,N,O}); there is no
universal sampler. It is also optional — hand-written theory personas
(e.g. economics/homo_silicus) skip it entirely.

  big5 — draw {E,A,C,N,O} specs from Big Five population norms
"""

from . import big5

__all__ = ["big5"]
