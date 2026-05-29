"""
One-to-one replication of Homo Silicus (Horton, Filippas & Manning 2023),
Experiment 1 — Kahneman, Knetsch & Thaler (1986) price-fairness task.

Faithful to kkt.py in github.com/johnjosephhorton/homo_silicus: direct prompts
(NO oTree), persona inline, the model completes a 1-4 fairness rating. We use
our OpenRouter transport only as the API; the prompt/persona/parse logic is
Horton's, verbatim.

Horton's setup: text-davinci-003, temperature 0, prices {16,20,40,100},
6 political personas, "raises" vs neutral "changes" framing.
Original KKT (1986): for $15 -> $20, ~82% rated it unfair/very unfair.
Expected pattern: left-leaning -> unfair, right-leaning -> acceptable;
fairness falls as the price rises (dose-response).
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from replicant.providers import openrouter
from replicant.env import load_dotenv

load_dotenv()

MODEL = "openai/gpt-4o"        # Horton's primary model in the updated paper
TEMPERATURE = 0                # Horton's setting (deterministic)
PRICES = [16, 20, 40, 100]
POLITICS = ["socialist", "leftist", "liberal", "moderate",
            "liberterian", "conservative"]   # "liberterian" sic, per Horton's code
LABELS = {1: "Completely Fair", 2: "Acceptable", 3: "Unfair", 4: "Very Unfair"}


def create_prompt(new_price, politics=None, neutral=False):
    """Horton's exact KKT prompt (kkt.py lines 16-31)."""
    action = "changes the price to" if neutral else "raises the price to"
    prompt = (
        f"A hardware store has been selling snow shovels for $15. "
        f"The morning after a large snowstorm, the store {action} ${new_price}. \n\n"
        "Please rate this action as:\n"
        "1) Completely Fair \n2) Acceptable\n3) Unfair \n4) Very Unfair\n\n"
    )
    if politics:
        prompt += f"You are a {politics}.\n"
    prompt += "What is your choice [1, 2, 3, or 4]:"
    return prompt


def get_rating(prompt):
    txt = openrouter.complete([{"role": "user", "content": prompt}],
                              MODEL, temperature=TEMPERATURE)
    m = re.search(r"[1-4]", txt or "")
    return int(m.group()) if m else None


def main():
    if not os.environ.get("OPEN_ROUTER_API_KEY"):
        sys.exit("Set OPEN_ROUTER_API_KEY")

    print(f"KKT price-fairness replication | {MODEL} | temp={TEMPERATURE}\n")
    print("Fairness rating by persona x price (1=Completely Fair .. 4=Very Unfair):\n")

    header = f"{'persona':<14}" + "".join(f"${p:<7}" for p in PRICES)
    print(header)
    print("-" * len(header))

    # baseline (no persona) + the 6 political personas, the "raises" framing
    rows = {}
    for politics in [None] + POLITICS:
        name = politics or "(none)"
        ratings = []
        for price in PRICES:
            r = get_rating(create_prompt(price, politics))
            ratings.append(r)
        rows[name] = ratings
        cells = "".join(f"{(str(r) if r else '-'):<8}" for r in ratings)
        print(f"{name:<14}{cells}")

    # The headline KKT comparison: the $20 case, % "unfair" (>=3)
    print(f"\nKKT(1986) human baseline for $15->$20: ~82% rated it unfair.")
    twenty = {name: rows[name][PRICES.index(20)] for name in rows}
    print("Our $20 ratings:", {k: LABELS.get(v, "?") for k, v in twenty.items()})

    print(f"\nCost: ${openrouter.get_cost():.4f}")


if __name__ == "__main__":
    main()
