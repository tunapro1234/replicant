"""
Homo Silicus — Horton, Filippas & Manning (2023, revised 2026)

Theory-grounded one-sentence personas for economic games.
Each persona maps to a known economic theory: inequity aversion,
efficiency maximization, or pure self-interest.

For the fairness task, political ideology personas are used instead.

Replication setup:
  Models:       text-davinci-003 (original), GPT-4o, Claude-Sonnet-3.5,
                Llama-3-70B, Deepseek (updated version)
  Temperature:  1.0 (original used 0 for completions)
  Observations: 100 per game per persona (Charness-Rabin)
  Calibration:  Mixture model: w_E*v_E + w_I*v_I + w_S*v_S ≈ v_human
                Optimized via constrained least squares

Sources:
  Paper:  Horton, J.J. et al. "Large Language Models as Simulated Economic
          Agents: What Can We Learn from Homo Silicus?"
          https://arxiv.org/abs/2301.07543
  Code:   https://github.com/johnjosephhorton/homo_silicus
  Prompts from experiments/charness_rabin/charness_rabin.py (lines 96-100)
          and experiments/kkt/kkt.py (lines 94-101)
"""

# --- Charness & Rabin allocation game personas ---
# Exact strings from charness_rabin.py line 96-100

ALLOCATION_PERSONAS = {
    "none": "",
    "inequity_averse": "You only care about fairness between players",
    "self_interested": "You only care about your own pay-off",
    "efficient": "You only care about the total pay-off of both players",
}

# --- Kahneman fairness task personas ---
# Exact strings from kkt.py line 94-101

POLITICAL_PERSONAS = {
    "socialist": "You are a socialist.",
    "leftist": "You are a leftist.",
    "liberal": "You are a liberal.",
    "moderate": "You are a moderate.",
    "libertarian": "You are a liberterian.",  # sic — typo preserved from original
    "conservative": "You are a conservative.",
}

# --- Charness & Rabin scenarios ---
# Exact payoffs from charness_rabin.py line 20-27
# (left_a, left_b) vs (right_a, right_b) where B is the decider

SCENARIOS = {
    "Berk29": {"left": (400, 400), "right": (750, 400)},
    "Barc2":  {"left": (400, 400), "right": (750, 375)},
    "Berk23": {"left": (800, 200), "right": (0, 0)},
    "Barc8":  {"left": (300, 600), "right": (700, 500)},
    "Berk15": {"left": (200, 700), "right": (600, 600)},
    "Berk26": {"left": (0, 800),   "right": (400, 400)},
}

# Paper's original models
MODELS = ["openai/gpt-3.5-turbo", "openai/gpt-4o"]


def build_prompt(persona_key: str, game: str = "allocation") -> str:
    """Build persona string for a Homo Silicus experiment.

    Args:
        persona_key: key from ALLOCATION_PERSONAS or POLITICAL_PERSONAS
        game: "allocation" or "fairness"
    """
    if game == "allocation":
        return ALLOCATION_PERSONAS[persona_key]
    elif game == "fairness":
        return POLITICAL_PERSONAS[persona_key]
    raise ValueError(f"Unknown game: {game}")


def all_allocation_personas() -> list[dict]:
    """Return all allocation personas with keys and prompts."""
    return [{"key": k, "prompt": v} for k, v in ALLOCATION_PERSONAS.items()]


def all_political_personas() -> list[dict]:
    """Return all political personas with keys and prompts."""
    return [{"key": k, "prompt": v} for k, v in POLITICAL_PERSONAS.items()]
