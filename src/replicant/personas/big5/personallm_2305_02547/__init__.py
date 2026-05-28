"""
PersonaLLM — Jiang, Zhang et al. (NAACL 2024 Findings)

Binary Big Five persona via system prompt. 2^5 = 32 possible personality types.
Each trait is either high or low, no continuous control.

Replication setup:
  Models:      gpt-3.5-turbo-0613, gpt-4-0613
  Temperature: 0.7 for persona behavior, 0.0 for evaluation
  Personas:    320 total (10 per each of 32 binary combos)
  Validation:  BFI-44 questionnaire + 800-word story writing
  Effect sizes: d = 1.56 to 7.81 (GPT-3.5), d = 4.22 to 6.30 (GPT-4)

Sources:
  Paper: Jiang, H. et al. "PersonaLLM: Investigating the Ability of Large
         Language Models to Express Personality Traits" (NAACL 2024 Findings)
         https://arxiv.org/abs/2305.02547
  Code:  https://github.com/hjian42/PersonaLLM
  Trait pairs from Section 3.1. System prompt from Figure 1.
"""

# Exact binary pairs from the paper (Section 3.1)
TRAIT_PAIRS = {
    "E": ("extroverted", "introverted"),
    "A": ("agreeable", "antagonistic"),
    "C": ("conscientious", "unconscientious"),
    "N": ("neurotic", "emotionally stable"),
    "O": ("open to experience", "closed to experience"),
}

# Paper's exact models
MODELS = ["openai/gpt-3.5-turbo", "openai/gpt-4o"]

# Paper's generation temperature
TEMPERATURE = 0.7

# BFI-44 story prompt from the paper
STORY_PROMPT = "Please share a personal story in 800 words. Do not explicitly mention your personality traits in the story."


def build_prompt(E=3.0, A=3.0, C=3.0, N=3.0, O=3.0) -> str:
    """Build persona system prompt from a big5 spec (each trait 1-5).

    PersonaLLM is binary, so scores are thresholded: >= 3.0 -> high pole,
    < 3.0 -> low pole. This lets the same {E,A,C,N,O} spec the sampler
    produces drive both PersonaLLM and (future) continuous methods.

    Returns: "You are a character who is [t1], [t2], [t3], [t4], and [t5]."
    """
    return _prompt_from_bools(E >= 3.0, A >= 3.0, C >= 3.0, N >= 3.0, O >= 3.0)


def _prompt_from_bools(e, a, c, n, o) -> str:
    words = []
    for trait, val in [("E", e), ("A", a), ("C", c), ("N", n), ("O", o)]:
        high, low = TRAIT_PAIRS[trait]
        words.append(high if val else low)
    return f"You are a character who is {', '.join(words[:-1])}, and {words[-1]}."


def all_personas() -> list[dict]:
    """Generate all 32 binary personality types.

    Returns list of dicts with keys: E, A, C, N, O (bool), prompt (str), label (str).
    """
    personas = []
    for e in [True, False]:
        for a in [True, False]:
            for c in [True, False]:
                for n in [True, False]:
                    for o in [True, False]:
                        prompt = _prompt_from_bools(e, a, c, n, o)
                        label = "".join([
                            "E+" if e else "E-",
                            "A+" if a else "A-",
                            "C+" if c else "C-",
                            "N+" if n else "N-",
                            "O+" if o else "O-",
                        ])
                        personas.append({
                            "E": e, "A": a, "C": c, "N": n, "O": o,
                            "prompt": prompt,
                            "label": label,
                        })
    return personas
