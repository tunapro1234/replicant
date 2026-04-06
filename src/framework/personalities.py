"""
PersonalityFactory — Generate EDSL Agents with Big Five personality traits.

Provides validated Big Five profiles and population generators.
Traits are scored 1 (very low) to 7 (very high).
"""

from edsl import Agent, AgentList


BIG5_CODEBOOK = {
    "openness": (
        "Openness to experience (1=very low, 7=very high). "
        "High: curious, creative, open to new ideas. "
        "Low: conventional, practical, routine-preferring."
    ),
    "conscientiousness": (
        "Conscientiousness (1=very low, 7=very high). "
        "High: organized, disciplined, dependable. "
        "Low: careless, impulsive, flexible."
    ),
    "extraversion": (
        "Extraversion (1=very low, 7=very high). "
        "High: outgoing, assertive, energetic. "
        "Low: reserved, quiet, solitary."
    ),
    "agreeableness": (
        "Agreeableness (1=very low, 7=very high). "
        "High: cooperative, trusting, helpful. "
        "Low: competitive, skeptical, self-interested."
    ),
    "neuroticism": (
        "Neuroticism (1=very low, 7=very high). "
        "High: anxious, moody, easily stressed. "
        "Low: calm, emotionally stable, resilient."
    ),
}

# Archetypal profiles — each emphasizes different trait combinations
ARCHETYPES = {
    "agreeable_conscientious": {
        "openness": 4, "conscientiousness": 7, "extraversion": 4,
        "agreeableness": 7, "neuroticism": 2,
    },
    "disagreeable_careless": {
        "openness": 4, "conscientiousness": 2, "extraversion": 4,
        "agreeableness": 2, "neuroticism": 5,
    },
    "extraverted_open": {
        "openness": 7, "conscientiousness": 4, "extraversion": 7,
        "agreeableness": 4, "neuroticism": 3,
    },
    "neurotic_introverted": {
        "openness": 3, "conscientiousness": 4, "extraversion": 2,
        "agreeableness": 4, "neuroticism": 7,
    },
    "balanced": {
        "openness": 4, "conscientiousness": 4, "extraversion": 4,
        "agreeableness": 4, "neuroticism": 4,
    },
}

DEFAULT_INSTRUCTION = (
    "You are a participant in an experiment. "
    "Your personality traits shape how you think and decide. "
    "Let your personality naturally influence your choices — "
    "act as a real person with these characteristics would."
)


class PersonalityFactory:
    """
    Usage:
        factory = PersonalityFactory()

        # Get all archetypes, 4 agents each
        agents = factory.create_population(per_archetype=4)

        # Get specific profiles
        agents = factory.create_agents("agreeable_conscientious", n=10)

        # Custom traits
        agents = factory.create_custom({"openness": 7, "agreeableness": 1}, n=5)

        # Plain agents with no traits
        agents = factory.create_default(n=20)
    """

    def __init__(self, instruction=None):
        self.instruction = instruction or DEFAULT_INSTRUCTION

    def create_agent(self, name, traits):
        """Create a single EDSL Agent with Big Five traits."""
        return Agent(
            name=name,
            traits=traits,
            codebook=BIG5_CODEBOOK,
            instruction=self.instruction,
        )

    def create_agents(self, archetype, n=1):
        """Create n agents from a named archetype."""
        if archetype not in ARCHETYPES:
            raise ValueError(f"Unknown archetype: {archetype}. Choose from: {list(ARCHETYPES.keys())}")
        traits = ARCHETYPES[archetype]
        return AgentList([
            self.create_agent(f"{archetype}_{i+1}", traits)
            for i in range(n)
        ])

    def create_population(self, per_archetype=4):
        """Create a balanced population with all archetypes."""
        agents = []
        for arch_name in ARCHETYPES:
            agents.extend(self.create_agents(arch_name, per_archetype))
        return AgentList(agents)

    def create_custom(self, traits, n=1, name_prefix="custom"):
        """Create agents with custom trait values."""
        return AgentList([
            self.create_agent(f"{name_prefix}_{i+1}", traits)
            for i in range(n)
        ])

    def create_default(self, n=10):
        """Create plain agents with no personality traits."""
        return AgentList([Agent(name=f"subject_{i+1}") for i in range(n)])

    @staticmethod
    def list_archetypes():
        """Print available archetypes and their traits."""
        for name, traits in ARCHETYPES.items():
            scores = " ".join(f"{k[0].upper()}={v}" for k, v in traits.items())
            print(f"  {name:<28s} {scores}")
