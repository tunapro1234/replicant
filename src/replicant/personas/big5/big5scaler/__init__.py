"""
Big5-Scaler (Cho & Cheong, 2025)

Three prompt variants that embed numeric trait scores into natural language.
Uses NEO PI-R facet framework (Costa & McCrae, 1995) — 5 domains, 30 facets.

The paper tested scales n=10,25,50,100. Simple prompt at n=10 had lowest RMSE.
For proportional scaling experiments they used n=100.

Generation settings from paper: temperature=1.0, top_p=0.8

Sources:
  Paper: Cho, G. & Cheong, Y.G. (2025). "Scaling Personality Control in
         LLMs with Big Five Scaler Prompts"
         https://arxiv.org/abs/2508.06149
  All prompts from Appendix B (verified against PDF).
  Facet definitions from Appendix A, Table 6 (NEO PI-R framework).
"""

# --- Domain-level descriptions (Simple prompt) ---

DOMAIN_DESCRIPTIONS = {
    "O": "People with high openness score are imaginative, curious, and creative.",
    "C": "People with high conscientiousness score are disciplined and dependable.",
    "E": "People with high extraversion score are outgoing, enthusiastic, and enjoy social interactions.",
    "A": "People with high agreeableness score prioritize harmony and positive relationships.",
    "N": "People with high neuroticism score are more emotionally reactive and prone to mood swings.",
}

DOMAIN_NAMES = {
    "O": "openness",
    "C": "conscientiousness",
    "E": "extraversion",
    "A": "agreeableness",
    "N": "neuroticism",
}

# --- Facet-level descriptions (Specific prompt) ---
# Each entry: (facet_key, description_sentence)
# Exact text from Appendix B of the paper.

FACETS = {
    "O": [
        ("fantasy", "People with high fantasy score tend to have a rich imagination and prefer abstract and creative thinking."),
        ("aesthetics", "Those with high aesthetics score have a deep interest in art and beauty, and they enjoy and are capable of appreciating and creating artistic expressions."),
        ("feelings", "The higher the feelings score, the more people seek to understand themselves deeply and pursue complex emotional experiences."),
        ("actions", "Those with high actions score enjoy trying new things such as travel, food, and culture."),
        ("ideas", "People with high ideas score are often interested in philosophical and scientific inquiries."),
        ("values", "Those with high values score are more likely to explore their own values rather than following fixed social standards."),
    ],
    "C": [
        ("dutifulness", "Individuals with high scores in dutifulness approach their tasks with care and dedication, and they strongly feel accountable for their actions."),
        ("self_discipline", "Those with high self-discipline score can suppress impulses and exercise the self-discipline necessary to stick to their plans."),
        ("achievement_striving", "People with high achievement-striving score tend to set goals and consistently work towards achieving them."),
        ("order", "Individuals with high order score value structure and organization and prioritize maintaining order in their daily life or work."),
        ("deliberation", "Those with high deliberation score take their time to gather and analyze information before making decisions."),
        ("competence", "People with high competence score have the ability to persist in the face of difficulty or adversity."),
    ],
    "E": [
        ("gregariousness", "People with high gregariousness score enjoy interacting with others and love meeting and conversing with new people."),
        ("activity", "Individuals with high activity score are always on the move and adapt better to dynamic environments than to static ones."),
        ("excitement_seeking", "Those with high excitement-seeking score enjoy new experiences and adventures, seeking strong sensory stimulation."),
        ("positive_emotions", "People who experience high positive emotions score frequently tend to be optimistic and lively, often feeling good and full of energy."),
        ("assertiveness", "Individuals with high assertiveness score tend to take leadership in situations and actively step up to solve problems."),
        ("warmth", "Those with high warmth score thrive in various social environments, enjoying the opportunity to meet new people and network."),
    ],
    "A": [
        ("altruism", "People with high altruism score find joy in helping others and tend to prioritize their needs."),
        ("trust", "Those with high trust score tend to be positive and trusting of others' words and actions."),
        ("compliance", "People with high compliance score seek to avoid conflict and pursue cooperation."),
        ("modesty", "Individuals with high modesty score are reluctant to boast or draw attention to themselves, respecting others and maintaining a modest attitude."),
        ("tender_mindedness", "Those with high tender-mindedness score can deeply understand others' emotions and perspectives, resonating with their pain or joy."),
        ("straightforwardness", "Individuals with high straightforwardness score are accepting of others' mistakes or shortcomings, striving to understand rather than criticize."),
    ],
    "N": [
        ("anxiety", "People with high anxiety score often tend to feel tense and worried."),
        ("angry_hostility", "Those with high angry hostility score are quick to become frustrated or upset when faced with obstacles or unfair treatment."),
        ("depression", "Individuals with high depression score frequently feel sad or discouraged, sometimes losing hope in life."),
        ("self_consciousness", "People with high self-consciousness score frequently lose confidence in themselves and tend to evaluate themselves negatively."),
        ("impulsiveness", "Individuals with high impulsiveness score experience frequent emotional instability, with their moods often shifting rapidly."),
        ("vulnerability", "People with high vulnerability score feel overwhelmed easily in difficult situations and can be greatly disturbed by even small problems."),
    ],
}

CLOSING = "From now on, you are an agent with this personality, and you should respond based on this personality."

DOMAIN_ORDER = ["O", "C", "E", "A", "N"]


def build_prompt(E=5, A=5, C=5, N=5, O=5, scale=10, variant="simple") -> str:
    if variant == "simple":
        return _simple({"O": O, "C": C, "E": E, "A": A, "N": N}, scale)
    elif variant == "specific":
        return _specific({"O": O, "C": C, "E": E, "A": A, "N": N}, scale)
    elif variant == "simspec":
        return _simspec({"O": O, "C": C, "E": E, "A": A, "N": N}, scale)
    raise ValueError(f"Unknown variant: {variant}. Choose: simple, specific, simspec")


def build_prompt_facets(facets: dict, scale=10, variant="specific") -> str:
    """Build prompt with individual facet scores (for Specific/Simspec).
    facets: dict mapping facet_key -> score (e.g. {"fantasy": 7, "aesthetics": 3, ...})
    """
    if variant == "specific":
        return _specific_facets(facets, scale)
    elif variant == "simspec":
        return _simspec_facets(facets, scale)
    raise ValueError(f"Facet-level prompts only for specific/simspec, not {variant}")


# --- Simple: 5 domain descriptions + scores ---

def _simple(scores, scale):
    lines = []
    for d in DOMAIN_ORDER:
        desc = DOMAIN_DESCRIPTIONS[d]
        name = DOMAIN_NAMES[d]
        lines.append(f"{desc} Your {name} score is {scores[d]} out of {scale}.")
    lines.append(CLOSING)
    return "\n".join(lines)


# --- Specific: 30 facet descriptions + scores (derived from domain) ---

def _specific(scores, scale):
    lines = []
    for d in DOMAIN_ORDER:
        val = scores[d]
        for facet_key, desc in FACETS[d]:
            lines.append(f"{desc} Your {facet_key.replace('_', '-')} score is {val} out of {scale}.")
    lines.append(CLOSING)
    return "\n".join(lines)


# --- Specific with individual facet scores ---

def _specific_facets(facets, scale):
    lines = []
    for d in DOMAIN_ORDER:
        for facet_key, desc in FACETS[d]:
            val = facets.get(facet_key, scale // 2)
            lines.append(f"{desc} Your {facet_key.replace('_', '-')} score is {val} out of {scale}.")
    lines.append(CLOSING)
    return "\n".join(lines)


# --- Simspec: facets + domain summaries inserted after each trait group ---

def _simspec(scores, scale):
    lines = []
    for d in DOMAIN_ORDER:
        val = scores[d]
        for facet_key, desc in FACETS[d]:
            lines.append(f"{desc} Your {facet_key.replace('_', '-')} score is {val} out of {scale}.")
        # Domain summary after facets (this is what makes Simspec different)
        lines.append(f"{DOMAIN_DESCRIPTIONS[d]} Your {DOMAIN_NAMES[d]} score is {val} out of {scale}.")
    lines.append(CLOSING)
    return "\n".join(lines)


# --- Simspec with individual facet scores ---

def _simspec_facets(facets, scale, domain_scores=None):
    lines = []
    for d in DOMAIN_ORDER:
        for facet_key, desc in FACETS[d]:
            val = facets.get(facet_key, 5)
            lines.append(f"{desc} Your {facet_key.replace('_', '-')} score is {val} out of {scale}.")
        # Domain summary — average of facet scores if no explicit domain score
        if domain_scores and d in domain_scores:
            dval = domain_scores[d]
        else:
            fkeys = [fk for fk, _ in FACETS[d]]
            dval = round(sum(facets.get(k, 5) for k in fkeys) / len(fkeys))
        lines.append(f"{DOMAIN_DESCRIPTIONS[d]} Your {DOMAIN_NAMES[d]} score is {dval} out of {scale}.")
    lines.append(CLOSING)
    return "\n".join(lines)


def get_all_facet_keys() -> list[str]:
    """Return all 30 facet keys in domain order."""
    keys = []
    for d in DOMAIN_ORDER:
        for facet_key, _ in FACETS[d]:
            keys.append(facet_key)
    return keys
