"""
Personality validation: assign BFI-2-Expanded, measure with Mini-IPIP via EDSL.

Cross-instrument validation — uses two DIFFERENT psychometric instruments
so the LLM can't just parrot back the assignment.

  Assignment:   BFI-2-Expanded sentences (Soto & John, 2017)
  Measurement:  Mini-IPIP 20-item inventory (Donnellan et al., 2006)

Provides two validation modes:
  - level_validation: high/average/low classification, % match
  - continuous_validation: Pearson r, MAE, R² between assigned and measured

Usage:
    from replicant.personalities.validation import (
        run_level_validation, run_continuous_validation,
    )

    # Test 5 named profiles
    results = run_level_validation(model="stepfun/step-3.5-flash")

    # Test N agents with random trait scores
    results = run_continuous_validation(n=20, model="stepfun/step-3.5-flash")
"""

import math
import random

from edsl import Agent, AgentList, Model, QuestionLinearScale, Survey

from .factory import (
    PersonalityFactory, PROFILES, DOMAINS, POPULATION_NORMS,
    build_description, _score_to_weight,
)


# ── Mini-IPIP items (Donnellan et al., 2006) ─────────────────────────
# 20 items, 4 per domain, 1-5 Likert scale

MINI_IPIP = [
    # Extraversion
    {"id": 1,  "text": "Am the life of the party",                              "domain": "extraversion",      "reverse": False},
    {"id": 2,  "text": "Don't talk a lot",                                       "domain": "extraversion",      "reverse": True},
    {"id": 3,  "text": "Talk to a lot of different people at parties",          "domain": "extraversion",      "reverse": False},
    {"id": 4,  "text": "Keep in the background",                                "domain": "extraversion",      "reverse": True},
    # Agreeableness
    {"id": 5,  "text": "Sympathize with others' feelings",                      "domain": "agreeableness",     "reverse": False},
    {"id": 6,  "text": "Am not interested in other people's problems",          "domain": "agreeableness",     "reverse": True},
    {"id": 7,  "text": "Feel others' emotions",                                 "domain": "agreeableness",     "reverse": False},
    {"id": 8,  "text": "Am not really interested in others",                    "domain": "agreeableness",     "reverse": True},
    # Conscientiousness
    {"id": 9,  "text": "Get chores done right away",                            "domain": "conscientiousness", "reverse": False},
    {"id": 10, "text": "Often forget to put things back in their proper place", "domain": "conscientiousness", "reverse": True},
    {"id": 11, "text": "Like order",                                            "domain": "conscientiousness", "reverse": False},
    {"id": 12, "text": "Make a mess of things",                                 "domain": "conscientiousness", "reverse": True},
    # Neuroticism
    {"id": 13, "text": "Have frequent mood swings",                             "domain": "neuroticism",       "reverse": False},
    {"id": 14, "text": "Am relaxed most of the time",                           "domain": "neuroticism",       "reverse": True},
    {"id": 15, "text": "Get upset easily",                                      "domain": "neuroticism",       "reverse": False},
    {"id": 16, "text": "Seldom feel blue",                                      "domain": "neuroticism",       "reverse": True},
    # Openness
    {"id": 17, "text": "Have a vivid imagination",                              "domain": "openness",          "reverse": False},
    {"id": 18, "text": "Am not interested in abstract ideas",                   "domain": "openness",          "reverse": True},
    {"id": 19, "text": "Have difficulty understanding abstract ideas",          "domain": "openness",          "reverse": True},
    {"id": 20, "text": "Do not have a good imagination",                        "domain": "openness",          "reverse": True},
]


def build_mini_ipip_survey() -> Survey:
    """Build an EDSL survey with all 20 Mini-IPIP items as LinearScale questions."""
    questions = []
    for item in MINI_IPIP:
        q = QuestionLinearScale(
            question_name=f"ipip_{item['id']}",
            question_text=(
                f"Rate how accurately this describes you: \"{item['text']}\""
            ),
            question_options=[1, 2, 3, 4, 5],
            option_labels={
                1: "Very inaccurate",
                2: "Moderately inaccurate",
                3: "Neutral",
                4: "Moderately accurate",
                5: "Very accurate",
            },
        )
        questions.append(q)
    return Survey(questions=questions)


def score_results(df) -> dict:
    """Score Mini-IPIP responses into Big Five domain scores (1-5)."""
    scores = {}
    for domain in DOMAINS:
        items = [i for i in MINI_IPIP if i["domain"] == domain]
        total = 0
        for item in items:
            col = f"answer.ipip_{item['id']}"
            raw = df[col].iloc[0]
            if raw is None or str(raw) == "nan":
                raw = 3  # neutral fallback
            else:
                raw = float(raw)
            if item["reverse"]:
                total += (6 - raw)
            else:
                total += raw
        scores[domain] = total / len(items)
    return scores


def level_from_score(score: float) -> str:
    """Convert 1-5 score to high/average/low classification."""
    if score >= 3.75:
        return "high"
    elif score <= 2.25:
        return "low"
    return "average"


def weight_to_score(weight: float) -> float:
    """Convert -3 to +3 weight back to 1-5 scale."""
    return (weight / 1.5) + 3.0


# ── Level validation (binary high/avg/low matching) ─────────────────

def run_level_validation(model: str = "stepfun/step-3.5-flash",
                         profiles: list[str] = None) -> dict:
    """
    Test 5 named profiles via Mini-IPIP and compute % match at the
    high/average/low classification level.

    Returns:
        {"profile_results": [...], "overall_match_pct": float}
    """
    profiles_to_test = profiles or list(PROFILES.keys())
    edsl_model = Model(model, service_name="open_router", max_tokens=100000)
    survey = build_mini_ipip_survey()
    factory = PersonalityFactory()

    print(f"\n{'='*65}", flush=True)
    print("LEVEL VALIDATION (high / average / low matching)", flush=True)
    print(f"Model: {model}", flush=True)
    print(f"{'='*65}\n", flush=True)

    all_results = []

    for profile_name in profiles_to_test:
        agent = factory.create_profile(profile_name, n=1)[0]
        assigned = PROFILES[profile_name]

        assigned_levels = {}
        for d, w in assigned.items():
            if w >= 1.5:
                assigned_levels[d] = "high"
            elif w <= -1.5:
                assigned_levels[d] = "low"
            else:
                assigned_levels[d] = "average"

        print(f"Profile: {profile_name}", flush=True)

        r = survey.by(agent).by(edsl_model).run()
        df = r.to_pandas()
        scores = score_results(df)
        measured_levels = {d: level_from_score(s) for d, s in scores.items()}
        matches = sum(1 for d in DOMAINS if assigned_levels[d] == measured_levels[d])

        scores_str = " ".join(f"{d[:3]}={s:.1f}" for d, s in scores.items())
        print(f"  Measured: {scores_str}", flush=True)
        print(f"  Match:    {matches}/5\n", flush=True)

        all_results.append({
            "profile": profile_name,
            "assigned_levels": assigned_levels,
            "measured_scores": scores,
            "measured_levels": measured_levels,
            "matches": matches,
        })

    total = sum(r["matches"] for r in all_results)
    possible = len(all_results) * 5
    overall = total / possible if possible > 0 else 0

    print(f"\nOverall: {total}/{possible} ({overall*100:.0f}%)", flush=True)

    return {
        "profile_results": all_results,
        "overall_match_pct": overall,
        "matches": total,
        "possible": possible,
    }


# ── Continuous validation (Pearson r, MAE, R²) ──────────────────────

def run_continuous_validation(model: str = "stepfun/step-3.5-flash",
                              n: int = 20, seed: int = 42) -> dict:
    """
    Sample N agents from population norms and measure each via Mini-IPIP.
    Compute Pearson r, R², MAE, and bias per domain plus pooled.

    Returns:
        {"paired_data": [...], "metrics": {...}, "pooled": {...}}
    """
    print(f"\n{'='*70}", flush=True)
    print("CONTINUOUS PERSONALITY VALIDATION", flush=True)
    print(f"Model: {model} | N: {n} | seed: {seed}", flush=True)
    print(f"{'='*70}\n", flush=True)

    # Generate N agents with random trait scores
    rng = random.Random(seed)
    agents_data = []

    for i in range(n):
        scores_1to5 = {}
        weights = {}
        for domain, norms in POPULATION_NORMS.items():
            score = rng.gauss(norms["mean"], norms["sd"])
            score = max(1.0, min(5.0, score))
            scores_1to5[domain] = score
            weights[domain] = _score_to_weight(score)

        description = build_description(weights)
        agent = Agent(
            name=f"agent_{i+1}",
            traits={"personality": description},
            instruction=(
                "You are a participant in a psychology study. "
                "Your personality description below reflects who you are. "
                "Let it naturally shape your responses — answer as a real "
                "person with this personality would."
            ),
        )
        agents_data.append((f"agent_{i+1}", scores_1to5, agent))

    # Run Mini-IPIP on each agent
    edsl_model = Model(model, service_name="open_router", max_tokens=100000)
    survey = build_mini_ipip_survey()

    print(f"Running Mini-IPIP on {n} agents...\n", flush=True)
    paired_data = []

    for name, assigned, agent in agents_data:
        print(f"  {name}...", flush=True)
        r = survey.by(agent).by(edsl_model).run()
        df = r.to_pandas()
        measured = score_results(df)

        for domain in DOMAINS:
            paired_data.append({
                "agent": name, "domain": domain,
                "assigned": assigned[domain], "measured": measured[domain],
            })

        print(
            "    " + " ".join(
                f"{d[:3]}: {assigned[d]:.1f}→{measured[d]:.1f}"
                for d in DOMAINS
            ),
            flush=True,
        )

    # Compute per-domain metrics
    print(f"\n{'='*70}", flush=True)
    print("METRICS BY DOMAIN", flush=True)
    print(f"{'='*70}", flush=True)
    print(f"{'Domain':<22s} {'r':>8s} {'r²':>8s} {'MAE':>8s} {'Bias':>8s}", flush=True)
    print("-" * 60, flush=True)

    metrics = {}
    for domain in DOMAINS:
        rows = [p for p in paired_data if p["domain"] == domain]
        a = [p["assigned"] for p in rows]
        m = [p["measured"] for p in rows]
        r, r2, mae, bias = _compute_metrics(a, m)
        metrics[domain] = {"r": r, "r_squared": r2, "mae": mae, "bias": bias, "n": len(a)}
        print(f"{domain:<22s} {r:>+8.3f} {r2:>8.3f} {mae:>8.3f} {bias:>+8.3f}", flush=True)

    # Pooled
    all_a = [p["assigned"] for p in paired_data]
    all_m = [p["measured"] for p in paired_data]
    pr, pr2, pmae, pbias = _compute_metrics(all_a, all_m)

    print("-" * 60, flush=True)
    print(f"{'POOLED':<22s} {pr:>+8.3f} {pr2:>8.3f} {pmae:>8.3f} {pbias:>+8.3f}", flush=True)
    print(flush=True)

    return {
        "paired_data": paired_data,
        "metrics": metrics,
        "pooled": {"r": pr, "r_squared": pr2, "mae": pmae, "bias": pbias},
    }


def _compute_metrics(assigned: list, measured: list) -> tuple:
    """Compute Pearson r, R², MAE, and bias."""
    n = len(assigned)
    if n == 0:
        return float("nan"), float("nan"), float("nan"), float("nan")

    mean_a = sum(assigned) / n
    mean_m = sum(measured) / n
    cov = sum((a - mean_a) * (m - mean_m) for a, m in zip(assigned, measured)) / n
    var_a = sum((a - mean_a) ** 2 for a in assigned) / n
    var_m = sum((m - mean_m) ** 2 for m in measured) / n

    if var_a > 0 and var_m > 0:
        r = cov / (math.sqrt(var_a) * math.sqrt(var_m))
    else:
        r = float("nan")

    r2 = r * r if not math.isnan(r) else float("nan")
    mae = sum(abs(a - m) for a, m in zip(assigned, measured)) / n
    bias = mean_m - mean_a

    return r, r2, mae, bias
