"""
PersonaLLM (Jiang et al., NAACL 2024)
Binary adjective pairs per BFI-2 domain. Score > 3 = high, < 3 = low.
Prompt: "You are a character who is [adj1], [adj2], ..., and [adjN]."

Sources:
  Paper: Jiang, H. et al. "PersonaLLM: Investigating the Ability of Large
         Language Models to Express Personality Traits" (NAACL 2024 Findings)
         https://arxiv.org/abs/2305.02547
  Code:  https://github.com/hjian42/PersonaLLM
  Trait pairs from Section 3.1 of the paper.
"""

from ..bfi2 import DOMAINS

# Exact pairs from the PersonaLLM paper (Table in Section 3.1)
HIGH_LOW = {
    "E": ("extroverted", "introverted"),
    "A": ("agreeable", "antagonistic"),
    "C": ("conscientious", "unconscientious"),
    "N": ("neurotic", "emotionally stable"),
    "O": ("open to experience", "closed to experience"),
}


def build_prompt(E=3.0, A=3.0, C=3.0, N=3.0, O=3.0) -> str:
    scores = {"E": E, "A": A, "C": C, "N": N, "O": O}
    words = []
    for domain in ["E", "A", "C", "N", "O"]:
        high, low = HIGH_LOW[domain]
        words.append(high if scores[domain] >= 3.0 else low)
    return f"You are a character who is {', '.join(words[:-1])}, and {words[-1]}."
