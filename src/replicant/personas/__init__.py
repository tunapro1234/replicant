"""
Persona layer — turn a spec into a "person" (a system-prompt string).

Output contract is universal: every persona's build_prompt(...) returns a str
for the runner. Input contract is per-FAMILY, not universal:

  baseline/    — no spec (null persona)
  big5/        — spec is {E, A, C, N, O}, each 1-5 (paired with sampling.big5)
  economics/   — spec is a theory category (hand-picked, no sampler)
  edsl/        — spec is an arbitrary trait dict (rendered via edsl.Agent)

A sampler pairs with a family by producing that family's spec shape. There is
deliberately no cross-family persona interface — see the design note above.
"""
