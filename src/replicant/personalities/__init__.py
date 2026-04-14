from .factory import (
    PersonalityFactory,
    PROFILES,
    POPULATION_NORMS,
    DOMAINS,
    SENTENCES,
    build_description,
    blend_sentences,
    score_to_weight,
    # Top-level researcher API
    build_personality,
    sample_personalities,
    list_personalities,
)

__all__ = [
    # Top-level helpers (the friendly API)
    "build_personality",
    "sample_personalities",
    "list_personalities",
    # Lower-level
    "PersonalityFactory",
    "PROFILES",
    "POPULATION_NORMS",
    "DOMAINS",
    "SENTENCES",
    "build_description",
    "blend_sentences",
    "score_to_weight",
]
