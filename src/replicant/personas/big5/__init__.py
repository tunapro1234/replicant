"""
Big Five persona family.

Shared input contract: build_prompt(E, A, C, N, O) with each trait on 1-5.
All methods here consume the same spec (what sampling.big5 produces) and
interpret it their own way.

  bfi2       — the 60-item BFI-2 trait bank (data, not a persona method)
  personallm — binary adjectives, scores thresholded at 3.0 (arXiv:2305.02547)
"""

from . import bfi2
from .personallm_2305_02547 import build_prompt as personallm

__all__ = ["bfi2", "personallm"]
