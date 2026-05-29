"""
Phase 2a — one variable changed from charness_rabin.py: ADD oTree.

Same model (GPT-4o), same temperature (0), same theory personas, same 6
scenarios. The only difference: instead of Horton's direct prompt, each agent
plays the scenarios through our oTree pipeline (one 6-round session per persona).
We then recompute the calibration and check the weights still match the no-oTree
replication and the paper. If they diverge a lot, that's a finding to flag.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from replicant import play
from replicant.runners.otree import OTreeClient
from replicant.personas.economics.homo_silicus_2301_07543 import ALLOCATION_PERSONAS
from replicant.personas.economics.homo_silicus_2301_07543.calibrate import fit_weights
from replicant.env import load_dotenv

# reuse the human target + Horton's weights from the no-oTree script (same dir)
from charness_rabin import HUMAN_LEFT, HORTON_WEIGHTS

load_dotenv()

SERVER = "http://localhost:8000"
REST_KEY = "test-rest-key"
GAMES = ["Berk29", "Barc2", "Berk23", "Barc8", "Berk15", "Berk26"]  # oTree round order


def play_persona(persona_text, model, temperature):
    """Play one agent through the 6-round oTree C&R game; return 6 choices in order."""
    url = OTreeClient.create_session(SERVER, "charness_rabin", 1, REST_KEY)[0]
    result = play(url, persona_text, model, temperature=temperature)
    return [e["answers"]["choice"] for e in result["log"] if "answers" in e]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="openai/gpt-4o")
    p.add_argument("--temperature", type=float, default=0.0)
    args = p.parse_args()
    MODEL, TEMPERATURE = args.model, args.temperature

    if not os.environ.get("OPEN_ROUTER_API_KEY"):
        sys.exit("Set OPEN_ROUTER_API_KEY")

    print(f"Charness-Rabin via oTree | {MODEL} | temp={TEMPERATURE}\n")
    theory = ["efficient", "inequity_averse", "self_interested"]

    header = f"{'persona':<18}" + "".join(f"{g:<9}" for g in GAMES)
    print(header)
    print("-" * len(header))

    behavior = {}
    for p in theory:
        choices = play_persona(ALLOCATION_PERSONAS[p], MODEL, TEMPERATURE)
        if len(choices) != len(GAMES):
            print(f"  {p}: WARNING got {len(choices)} choices, expected {len(GAMES)}")
        behavior[p] = [1.0 if c == "Left" else 0.0 for c in choices]
        print(f"{p:<18}" + "".join(f"{c:<9}" for c in choices))

    target = [HUMAN_LEFT[g] for g in GAMES]
    weights, sse = fit_weights(behavior, target)
    rmse = (sse / len(GAMES)) ** 0.5

    print(f"\nCalibrated weights via oTree (RMSE {rmse:.3f}):")
    for p in theory:
        print(f"  {p:<18}{weights[p]:.0%}")
    print("\nFor comparison:")
    print("  no-oTree (GPT-4o)   efficient 44% / inequity 0% / self 56%")
    for model, w in HORTON_WEIGHTS.items():
        print(f"  Horton {model:<12}{w['efficient']:.0%} / {w['inequity_averse']:.0%} / "
              f"{w['self_interested']:.0%}")
    print(f"\nCost: $see-provider")


if __name__ == "__main__":
    main()
