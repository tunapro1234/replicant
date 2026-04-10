"""
Public Goods Game template — reusable EDSL surveys for VCM experiments.

Covers the standard components:
- Contribution decision (with/without punishment)
- Punishment rule voting
- Punishment decision (amount + target)

Each function returns an EDSL Survey + optional ScenarioList.
Papers plug in their specific parameters.
"""

from edsl import (
    QuestionFreeText,
    QuestionMultipleChoice,
    QuestionNumerical,
    Scenario,
    ScenarioList,
    Survey,
)


def contribution_survey(endowment, group_size, mpcr, regime_description=None):
    """
    Survey asking how much to contribute to the public good.

    If regime_description is None, creates a no-punishment baseline.
    """
    if regime_description:
        rule_text = f"\nPunishment rule: {regime_description} "
    else:
        rule_text = "\nThere is NO punishment mechanism in this round. "

    q = QuestionNumerical(
        question_name="contribution",
        question_text=(
            f"You are in a group of {group_size} people. "
            f"Each person receives {endowment} tokens. "
            f"Each person independently decides how many tokens to contribute to a group project. "
            f"For every token contributed, each group member (including you) receives {mpcr} tokens. "
            f"Tokens you keep remain yours."
            f"{rule_text}"
            f"\nHow many tokens (0 to {endowment}) do you contribute?"
        ),
        min_value=0,
        max_value=endowment,
    )
    return Survey(questions=[q])


def contribution_regime_survey(endowment, group_size, mpcr, regimes):
    """
    Survey for contribution under different punishment regimes.

    Args:
        regimes: dict of {regime_name: regime_description}

    Returns (Survey, ScenarioList) — one scenario per regime.
    """
    q = QuestionNumerical(
        question_name="contribution",
        question_text=(
            f"You are in a group of {group_size} people. "
            f"Each person receives {endowment} tokens. "
            f"For every token contributed, each member receives {mpcr} tokens. "
            "\nPunishment rule: {{ regime_description }} "
            f"\nHow many tokens (0 to {endowment}) do you contribute?"
        ),
        min_value=0,
        max_value=endowment,
    )
    scenarios = ScenarioList([
        Scenario({"regime_name": name, "regime_description": desc})
        for name, desc in regimes.items()
    ])
    return Survey(questions=[q]), scenarios


def voting_survey(punishment_ratio):
    """
    Survey asking whether to allow punishment of low/high contributors.
    Returns a Survey (no scenarios needed).
    """
    q_low = QuestionMultipleChoice(
        question_name="vote_punish_low",
        question_text=(
            "Your group will vote on punishment rules. "
            f"Punishment costs 1 token to the punisher and removes {punishment_ratio} "
            "tokens from the target. "
            "\nShould members be ALLOWED to punish those who contribute "
            "BELOW the group average?"
        ),
        question_options=["Yes", "No"],
    )
    q_high = QuestionMultipleChoice(
        question_name="vote_punish_high",
        question_text=(
            "Should members be ALLOWED to punish those who contribute "
            "ABOVE the group average?"
        ),
        question_options=["Yes", "No"],
    )
    return Survey(questions=[q_low, q_high])


def punishment_survey(endowment, group_size, mpcr, punishment_ratio, regimes, profiles):
    """
    Survey for punishment decisions under different regimes and contribution profiles.

    Args:
        regimes: dict {regime_name: description} (should exclude no_punishment)
        profiles: list of {"name": str, "others": str, "avg": float}

    Returns (Survey, ScenarioList).
    """
    q_amount = QuestionNumerical(
        question_name="punish_amount",
        question_text=(
            f"You are in a group of {group_size} with {endowment} tokens each. "
            f"For every token contributed, each member receives {mpcr} tokens. "
            "\nPunishment rule: {{ regime_description }} "
            "\nThe other members contributed: {{ others }} tokens. "
            "Group average: {{ avg }}. You contributed 15 tokens. "
            f"\nEach token you spend on punishment removes {punishment_ratio} "
            "tokens from the target. "
            "\nHow many tokens (0 to 5) do you spend on punishing?"
        ),
        min_value=0,
        max_value=5,
    )
    q_target = QuestionMultipleChoice(
        question_name="punish_target",
        question_text=(
            "Who do you primarily target with your punishment? "
            "Others contributed: {{ others }} (avg: {{ avg }})."
        ),
        question_options=[
            "Lowest contributor",
            "Below-average contributors",
            "Above-average contributors",
            "Highest contributor",
            "Nobody",
        ],
    )
    scenarios = ScenarioList([
        Scenario({
            "regime_name": rname,
            "regime_description": rdesc,
            "profile_name": p["name"],
            "others": p["others"],
            "avg": p["avg"],
        })
        for rname, rdesc in regimes.items()
        for p in profiles
    ])
    return Survey(questions=[q_amount, q_target]), scenarios
