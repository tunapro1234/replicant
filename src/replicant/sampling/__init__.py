"""
Sampling layer — produces person-specs that tell the persona layer WHAT to build.

A sampler outputs specs (e.g. trait dicts, demographic rows) drawn from a
population definition: published norms, a CSV of real respondents, a joint
demographic distribution, etc.

Contract: sampling is upstream and dumb about everything below it. It never
knows how a spec becomes a prompt, and it never knows about calibration —
that is the persona layer's job. A spec goes in one direction:

    sampling --(spec)--> persona --(prompt)--> runner --> provider

Sampling is optional: hand-written theory personas (e.g. Homo Silicus) skip it.
Some samplers may use the provider layer (e.g. generating Anthology backstories).
"""
