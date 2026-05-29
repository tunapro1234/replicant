"""
Big Five persona family.

Shared input contract: build_prompt(E, A, C, N, O) with each trait on 1-5.
Pairs with sampling.big5, which produces exactly that {E,A,C,N,O} spec.

  personallm — binary adjectives, scores thresholded at 3.0 (arXiv:2305.02547)
"""

from .personallm_2305_02547 import build_prompt as personallm

__all__ = ["personallm"]
