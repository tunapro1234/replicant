"""
PersonalityFactory — Generate BFI-2-Expanded personality descriptions.

Uses the calibrated sentence bank and blending approach from the personality
validation project (/srv/behave/personality/). Each domain has 7 intensity
levels (-3 to +3) with 3 sentences each. Fractional weights blend sentences
from adjacent levels for fine-grained control.

Validated at 84% domain-level alignment using cross-instrument measurement
(assign with BFI-2-Expanded, measure with Mini-IPIP).

References:
  - Soto & John (2017) — BFI-2
  - Donnellan et al. (2006) — Mini-IPIP
  - Huang et al. (2024) — BFI-2-Expanded format for LLMs
"""

import math
import random


# ── 7-level sentence bank per domain (-3 to +3) ─────────────────────
# From /srv/behave/personality/src/calibrate.py
# Each level has 3 sentences (one per facet)

SENTENCES = {
    "extraversion": {
        -3: [
            "I am someone who strongly avoids social situations and prefers complete solitude.",
            "I am someone who never takes charge and actively avoids leadership roles.",
            "I am someone who has very low energy and avoids activity whenever possible.",
        ],
        -2: [
            "I am someone who tends to be quiet and avoids social gatherings.",
            "I am someone who prefers to have others take charge.",
            "I am someone who is less active than other people.",
        ],
        -1: [
            "I am someone who is somewhat reserved, though not antisocial.",
            "I am someone who occasionally lets others lead.",
            "I am someone who has moderate energy, leaning quieter.",
        ],
        0: [
            "I am someone who sometimes is outgoing, but not always.",
            "I am someone who sometimes acts as a leader, but not always.",
            "I am someone who sometimes is full of energy, but not always.",
        ],
        1: [
            "I am someone who is fairly sociable and enjoys company.",
            "I am someone who sometimes takes the lead in groups.",
            "I am someone who has good energy most of the time.",
        ],
        2: [
            "I am someone who is outgoing, sociable.",
            "I am someone who is dominant, acts as a leader.",
            "I am someone who is full of energy.",
        ],
        3: [
            "I am someone who is extremely outgoing and thrives on social interaction.",
            "I am someone who always takes charge and naturally dominates groups.",
            "I am someone who has boundless energy and is always on the go.",
        ],
    },
    "agreeableness": {
        -3: [
            "I am someone who is cold, uncaring, and indifferent to others' suffering.",
            "I am someone who is frequently rude and dismissive toward others.",
            "I am someone who is deeply suspicious and always assumes the worst.",
        ],
        -2: [
            "I am someone who can be cold and uncaring.",
            "I am someone who is sometimes rude to others.",
            "I am someone who tends to find fault with others.",
        ],
        -1: [
            "I am someone who is not particularly warm, though not unkind.",
            "I am someone who can be blunt, sometimes to a fault.",
            "I am someone who is somewhat skeptical of others' motives.",
        ],
        0: [
            "I am someone who sometimes is compassionate, but not always.",
            "I am someone who sometimes is respectful, but not always.",
            "I am someone who sometimes assumes the best about people, but not always.",
        ],
        1: [
            "I am someone who is generally kind and considerate.",
            "I am someone who usually treats others with respect.",
            "I am someone who tends to give people the benefit of the doubt.",
        ],
        2: [
            "I am someone who is compassionate, has a soft heart.",
            "I am someone who is respectful, treats others with respect.",
            "I am someone who assumes the best about people.",
        ],
        3: [
            "I am someone who is deeply compassionate and always puts others first.",
            "I am someone who treats everyone with the utmost respect and kindness.",
            "I am someone who always sees the good in people, no matter what.",
        ],
    },
    "conscientiousness": {
        -3: [
            "I am someone who is extremely disorganized and lives in chaos.",
            "I am someone who cannot finish tasks and gives up at the first obstacle.",
            "I am someone who is very careless and unreliable.",
        ],
        -2: [
            "I am someone who tends to be disorganized.",
            "I am someone who has difficulty getting started on tasks.",
            "I am someone who can be somewhat careless.",
        ],
        -1: [
            "I am someone who is not particularly organized, though not messy.",
            "I am someone who sometimes procrastinates.",
            "I am someone who is occasionally careless with details.",
        ],
        0: [
            "I am someone who sometimes keeps things tidy, but not always.",
            "I am someone who sometimes is persistent, but not always.",
            "I am someone who sometimes is reliable, but not always.",
        ],
        1: [
            "I am someone who generally keeps things in order.",
            "I am someone who usually follows through on tasks.",
            "I am someone who is mostly dependable.",
        ],
        2: [
            "I am someone who keeps things neat and tidy.",
            "I am someone who is persistent, works until the task is finished.",
            "I am someone who is reliable, can always be counted on.",
        ],
        3: [
            "I am someone who is meticulously organized and never tolerates disorder.",
            "I am someone who is relentlessly persistent and never leaves a task incomplete.",
            "I am someone who is unfailingly reliable in every situation.",
        ],
    },
    "neuroticism": {
        -3: [
            "I am someone who never worries and is immune to stress.",
            "I am someone who never feels sad or down, always completely content.",
            "I am someone who is unshakably calm and never gets emotional.",
        ],
        -2: [
            "I am someone who is relaxed, handles stress well.",
            "I am someone who feels secure, comfortable with self.",
            "I am someone who is emotionally stable, not easily upset.",
        ],
        -1: [
            "I am someone who doesn't worry much, though not completely carefree.",
            "I am someone who is generally content and secure.",
            "I am someone who is fairly even-tempered most of the time.",
        ],
        0: [
            "I am someone who sometimes worries, but not always.",
            "I am someone who sometimes feels down, but not always.",
            "I am someone who sometimes gets emotional, but not always.",
        ],
        1: [
            "I am someone who tends to worry more than average.",
            "I am someone who sometimes feels a bit down or blue.",
            "I am someone who can be somewhat sensitive emotionally.",
        ],
        2: [
            "I am someone who worries a lot.",
            "I am someone who tends to feel depressed, blue.",
            "I am someone who is temperamental, gets emotional easily.",
        ],
        3: [
            "I am someone who is consumed by worry and anxiety constantly.",
            "I am someone who frequently feels deeply depressed and hopeless.",
            "I am someone who is extremely volatile and emotionally unstable.",
        ],
    },
    "openness": {
        -3: [
            "I am someone who has absolutely no interest in art, music, or literature.",
            "I am someone who actively avoids abstract thinking and complex ideas.",
            "I am someone who has no creativity or imagination whatsoever.",
        ],
        -2: [
            "I am someone who has few artistic interests.",
            "I am someone who has little interest in abstract ideas.",
            "I am someone who has little creativity.",
        ],
        -1: [
            "I am someone who has limited interest in the arts.",
            "I am someone who prefers practical thinking over abstract ideas.",
            "I am someone who is not particularly creative or imaginative.",
        ],
        0: [
            "I am someone who sometimes appreciates art and music, but not always.",
            "I am someone who sometimes enjoys deep thinking, but not always.",
            "I am someone who sometimes comes up with new ideas, but not always.",
        ],
        1: [
            "I am someone who has some appreciation for art and culture.",
            "I am someone who occasionally enjoys exploring abstract ideas.",
            "I am someone who can be somewhat creative at times.",
        ],
        2: [
            "I am someone who is fascinated by art, music, or literature.",
            "I am someone who is complex, a deep thinker.",
            "I am someone who is original, comes up with new ideas.",
        ],
        3: [
            "I am someone who is passionately devoted to art, music, and literature.",
            "I am someone who constantly seeks out complex, abstract ideas.",
            "I am someone who is extraordinarily creative and always generating new ideas.",
        ],
    },
}

DOMAINS = ["extraversion", "agreeableness", "conscientiousness", "neuroticism", "openness"]

# ── Profiles (uncalibrated — raw BFI-2-Expanded levels) ──────────────
# high=+2, low=-2, average=0 on the sentence bank scale
# No pre-calibration: document any bias rather than compensating for it

PROFILES = {
    "cooperative": {
        "extraversion": 0, "agreeableness": 2, "conscientiousness": 2,
        "neuroticism": -2, "openness": 0,
    },
    "selfish": {
        "extraversion": 0, "agreeableness": -2, "conscientiousness": -2,
        "neuroticism": 2, "openness": 0,
    },
    "leader": {
        "extraversion": 2, "agreeableness": 0, "conscientiousness": 2,
        "neuroticism": -2, "openness": 2,
    },
    "anxious": {
        "extraversion": -2, "agreeableness": 0, "conscientiousness": 0,
        "neuroticism": 2, "openness": -2,
    },
    "average": {
        "extraversion": 0, "agreeableness": 0, "conscientiousness": 0,
        "neuroticism": 0, "openness": 0,
    },
}

# Population norms (US adults, 1-5 Mini-IPIP scale)
POPULATION_NORMS = {
    "extraversion":      {"mean": 3.3, "sd": 0.75},
    "agreeableness":     {"mean": 3.8, "sd": 0.60},
    "conscientiousness": {"mean": 3.7, "sd": 0.65},
    "neuroticism":       {"mean": 2.8, "sd": 0.75},
    "openness":          {"mean": 3.6, "sd": 0.65},
}

DEFAULT_INSTRUCTION = (
    "You are a participant in an experiment. "
    "Your personality description below reflects who you are. "
    "Let it naturally shape your decisions and reasoning — "
    "act as a real person with this personality would."
)


# ── Sentence blending ────────────────────────────────────────────────

def blend_sentences(domain, weight):
    """
    Get sentences for a fractional weight by mixing adjacent integer levels.
    Each integer level has 3 sentences. For fractional weights we pick
    from the two nearest levels proportionally.
    """
    weight = max(-3.0, min(3.0, weight))
    lo = int(math.floor(weight))
    hi = int(math.ceil(weight))

    if lo == hi:
        return list(SENTENCES[domain][lo])

    frac = weight - lo
    n_hi = round(frac * 3)
    n_lo = 3 - n_hi

    return SENTENCES[domain][lo][:n_lo] + SENTENCES[domain][hi][:n_hi]


def build_description(weights):
    """Build full personality description from weight dict {domain: float}."""
    lines = []
    for domain in DOMAINS:
        lines.extend(blend_sentences(domain, weights[domain]))
    return "\n".join(lines)


def score_to_weight(score):
    """Convert 1-5 Mini-IPIP score to -3 to +3 sentence-bank weight."""
    return (score - 3.0) * 1.5


# Backwards-compat alias (was previously private)
_score_to_weight = score_to_weight


# ── Top-level helpers (researcher-friendly API) ─────────────────────

def build_personality(
    extraversion: float = 3.0,
    agreeableness: float = 3.0,
    conscientiousness: float = 3.0,
    neuroticism: float = 3.0,
    openness: float = 3.0,
) -> str:
    """
    Build a single personality description from explicit OCEAN scores.

    All scores are on the 1-5 scale (3.0 = average, 5.0 = high, 1.0 = low).
    Returns the personality description as a string.

    Example:
        # A highly agreeable, low-neuroticism agent
        desc = build_personality(
            agreeableness=4.5,
            neuroticism=1.5,
        )
    """
    weights = {
        "extraversion": score_to_weight(extraversion),
        "agreeableness": score_to_weight(agreeableness),
        "conscientiousness": score_to_weight(conscientiousness),
        "neuroticism": score_to_weight(neuroticism),
        "openness": score_to_weight(openness),
    }
    return build_description(weights)


def sample_personalities(
    n: int = 20,
    seed: int = None,
    extraversion: float = None,
    agreeableness: float = None,
    conscientiousness: float = None,
    neuroticism: float = None,
    openness: float = None,
    sd_scale: float = 1.0,
) -> list[str]:
    """
    Sample N personality descriptions from population norms.

    By default samples from US adult Big Five norms (Soto & John, 2017).
    To skew the population on a trait, pass that trait as a kwarg — it
    overrides the population mean for that trait.

    Args:
        n: number of personalities to sample
        seed: random seed for reproducibility
        extraversion, agreeableness, ...: override the population mean
            for that trait (1-5 scale). Leave as None to use the default.
        sd_scale: scale factor for standard deviations (1.0 = default,
            0.0 = no variance, 2.0 = double variance)

    Returns:
        list of personality description strings (one per agent)

    Examples:
        # Default population
        personalities = sample_personalities(n=50)

        # All disagreeable
        personalities = sample_personalities(n=50, agreeableness=1.5)

        # Extreme low neuroticism, fixed exactly
        personalities = sample_personalities(n=50, neuroticism=1.0, sd_scale=0.0)

        # High variance population
        personalities = sample_personalities(n=50, sd_scale=2.0)
    """
    rng = random.Random(seed)
    overrides = {
        "extraversion": extraversion,
        "agreeableness": agreeableness,
        "conscientiousness": conscientiousness,
        "neuroticism": neuroticism,
        "openness": openness,
    }

    personalities = []
    for _ in range(n):
        weights = {}
        for domain, norms in POPULATION_NORMS.items():
            mean = overrides[domain] if overrides[domain] is not None else norms["mean"]
            sd = norms["sd"] * sd_scale
            score = rng.gauss(mean, sd) if sd > 0 else mean
            score = max(1.0, min(5.0, score))
            weights[domain] = score_to_weight(score)
        personalities.append(build_description(weights))
    return personalities


def list_personalities(personalities: list[str], domain_scores: list[dict] = None):
    """Pretty-print a list of personality descriptions for inspection."""
    for i, desc in enumerate(personalities, 1):
        print(f"\n{'='*60}")
        print(f"Personality {i}")
        if domain_scores and i <= len(domain_scores):
            print(" ".join(f"{d[:3]}={s:.1f}" for d, s in domain_scores[i-1].items()))
        print(f"{'='*60}")
        print(desc)


# ── PersonalityFactory ───────────────────────────────────────────────

class PersonalityFactory:
    """
    Generate personality descriptions from BFI-2-Expanded sentence bank.

    Usage:
        factory = PersonalityFactory()

        # Named profiles
        descriptions = factory.create_profile("cooperative", n=5)

        # All profiles, balanced
        descriptions = factory.create_population(per_profile=4)

        # Random from population norms
        descriptions = factory.create_random_population(n=20)
    """

    def __init__(self, instruction=None):
        self.instruction = instruction or DEFAULT_INSTRUCTION

    def create_profile(self, profile_name, n=1):
        if profile_name not in PROFILES:
            raise ValueError(f"Unknown profile: {profile_name}. Choose from: {list(PROFILES.keys())}")
        weights = PROFILES[profile_name]
        return [build_description(weights) for _ in range(n)]

    def create_population(self, per_profile=4):
        descriptions = []
        for name in PROFILES:
            descriptions.extend(self.create_profile(name, per_profile))
        return descriptions

    def create_random_population(self, n=20, seed=None, mean_overrides=None,
                                  sd_overrides=None):
        """
        Create a population sampled from Big Five distributions.

        Args:
            n: number of personality descriptions
            seed: random seed
            mean_overrides: dict to override population means, e.g.
                {"agreeableness": 1.5} for a low-agreeableness population
            sd_overrides: dict to override standard deviations
        """
        rng = random.Random(seed)
        mean_overrides = mean_overrides or {}
        sd_overrides = sd_overrides or {}

        descriptions = []
        for i in range(n):
            weights = {}
            for domain, norms in POPULATION_NORMS.items():
                mean = mean_overrides.get(domain, norms["mean"])
                sd = sd_overrides.get(domain, norms["sd"])
                score = rng.gauss(mean, sd)
                score = max(1.0, min(5.0, score))
                weights[domain] = _score_to_weight(score)
            descriptions.append(build_description(weights))
        return descriptions

    def create_custom(self, weights, n=1):
        return [build_description(weights) for _ in range(n)]

    def create_default(self, n=10):
        return [""] * n

    @staticmethod
    def list_profiles():
        for name, weights in PROFILES.items():
            w_str = " ".join(f"{d[:3]}={w:+d}" for d, w in weights.items())
            print(f"  {name:<15s}: {w_str}")

    @staticmethod
    def show_description(profile_name):
        if profile_name not in PROFILES:
            raise ValueError(f"Unknown profile: {profile_name}")
        print(build_description(PROFILES[profile_name]))
