"""
One-to-one replication of Homo Silicus (Horton, Filippas & Manning 2023),
Experiment 2 — Charness & Rabin (2002) allocation "dictator" games.

Faithful to charness_rabin.py in github.com/johnjosephhorton/homo_silicus:
direct prompts (NO oTree), Person B chooses Left/Right across 6 scenarios under
each theory persona. Then we calibrate a mixture of theory personas to match the
human choice proportions (Horton Sec 2.2.1) and compare weights to the paper.

Horton's setup: text-davinci-003, temperature 0, 6 scenarios, 4 personas.
Finding: persona-conditioned agents follow their theory almost perfectly; a
calibrated mixture matches human aggregates and generalizes out-of-sample.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from replicant.providers import openrouter
from replicant.personas.economics.homo_silicus_2301_07543.calibrate import (
    fit_weights, population,
)
from replicant.env import load_dotenv

load_dotenv()

MODEL = "openai/gpt-4o"
TEMPERATURE = 0

# Horton's exact scenarios: name -> ((left_a, left_b), (right_a, right_b))
# a = Person A's payoff, b = the decider's (Person B's) payoff.
SCENARIOS = {
    "Berk29": ((400, 400), (750, 400)),
    "Barc2":  ((400, 400), (750, 375)),
    "Berk23": ((800, 200), (0, 0)),
    "Barc8":  ((300, 600), (700, 500)),
    "Berk15": ((200, 700), (600, 600)),
    "Berk26": ((0, 800),   (400, 400)),
}

# Horton's exact personas (charness_rabin.py lines 96-100)
PERSONAS = {
    "none": "",
    "inequity_averse": "You only care about fairness between players",
    "self_interested": "You only care about your own pay-off",
    "efficient": "You only care about the total pay-off of both players",
}

# Human proportion choosing the first ("Left") option, per game.
# Source: Charness & Rabin (2002, QJE 117(3)), game-by-game results table.
HUMAN_LEFT = {
    "Berk29": 0.31, "Barc2": 0.52, "Berk23": 1.00,
    "Barc8": 0.67, "Berk15": 0.27, "Berk26": 0.78,
}

# Calibrated mixture weights Horton reports (theory personas E/I/S), for comparison.
HORTON_WEIGHTS = {
    "GPT-4o":           {"efficient": 0.37, "inequity_averse": 0.10, "self_interested": 0.53},
    "Claude-3.5":       {"efficient": 0.44, "inequity_averse": 0.00, "self_interested": 0.56},
    "Llama-3-70B":      {"efficient": 0.49, "inequity_averse": 0.00, "self_interested": 0.51},
    "Deepseek":         {"efficient": 0.44, "inequity_averse": 0.00, "self_interested": 0.56},
}


def create_prompt(scenario, personality):
    """Horton's exact allocation prompt (charness_rabin.py lines 29-38)."""
    (left_a, left_b), (right_a, right_b) = scenario
    return (
        "You are deciding on allocation for yourself and another person, Person A. \n"
        f"{personality}\n\n"
        f"    Option Left:  You get ${left_b}, Person A gets ${left_a}\n"
        f"    Option Right: You get ${right_b}, Person A gets ${right_a}\n\n"
        "    What do you choose, with one word [Left, Right]?"
    )


def get_choice(scenario, personality):
    txt = openrouter.complete([{"role": "user", "content": create_prompt(scenario, personality)}],
                              MODEL, temperature=TEMPERATURE)
    return "Left" if "left" in (txt or "").lower() else "Right"


def main():
    if not os.environ.get("OPEN_ROUTER_API_KEY"):
        sys.exit("Set OPEN_ROUTER_API_KEY")

    print(f"Charness-Rabin replication | {MODEL} | temp={TEMPERATURE}\n")
    games = list(SCENARIOS)
    header = f"{'persona':<18}" + "".join(f"{g:<9}" for g in games)
    print(header)
    print("-" * len(header))

    # choices[persona] = {game: "Left"/"Right"}
    choices = {}
    for pname, ptext in PERSONAS.items():
        row = {g: get_choice(SCENARIOS[g], ptext) for g in games}
        choices[pname] = row
        print(f"{pname:<18}" + "".join(f"{row[g]:<9}" for g in games))

    print(f"\nCost: ${openrouter.get_cost():.4f}")

    # --- Calibration (Horton Sec 2.2.1) ---
    # Each theory persona -> binary vector (1 if it chose Left in each game).
    # Fit a simplex mixture to the human "proportion chose Left" vector.
    theory = ["efficient", "inequity_averse", "self_interested"]
    target = [HUMAN_LEFT[g] for g in games]
    behavior = {p: [1.0 if choices[p][g] == "Left" else 0.0 for g in games]
                for p in theory}

    weights, sse = fit_weights(behavior, target)
    pred = [sum(weights[p] * behavior[p][i] for p in theory) for i in range(len(games))]

    print("\n=== Calibration: mixture of theory personas -> human choice vector ===")
    print(f"{'game':<10}{'human':<8}{'mixture':<9}")
    for i, g in enumerate(games):
        print(f"{g:<10}{target[i]:<8.2f}{pred[i]:<9.2f}")
    rmse = (sse / len(games)) ** 0.5
    print(f"\nFitted weights (RMSE {rmse:.3f}):")
    for p in theory:
        print(f"  {p:<18}{weights[p]:.0%}")
    print("\nHorton's reported weights (E / I / S):")
    for model, w in HORTON_WEIGHTS.items():
        print(f"  {model:<14}{w['efficient']:.0%} / {w['inequity_averse']:.0%} / "
              f"{w['self_interested']:.0%}")
    return choices


if __name__ == "__main__":
    main()
