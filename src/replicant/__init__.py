"""
replicant — LLM-based replication framework for behavioral economics experiments.

Provides:
- BehavioralExperiment: multi-part EDSL experiment runner
- PersonalityFactory: BFI-2-Expanded personality generator
- PaperComparison: simulation vs published results comparison
- oTree integration: LLM bots that play through real oTree experiments

Two pipelines:
  1. EDSL pipeline (single-shot, fast)
  2. oTree pipeline (multi-round, group-aware)

Usage:
    from replicant import BehavioralExperiment, PersonalityFactory

    factory = PersonalityFactory()
    agents = factory.create_random_population(n=50)

    exp = BehavioralExperiment("my_experiment", model="stepfun/step-3.5-flash")
    exp.add_part("baseline", contribution_survey(20, 5, 0.4))
    results = exp.run(agents)
"""

from .experiments.runner import BehavioralExperiment
from .experiments.comparison import PaperComparison
from .personalities.factory import PersonalityFactory

__version__ = "0.2.0"
__all__ = ["BehavioralExperiment", "PaperComparison", "PersonalityFactory"]
