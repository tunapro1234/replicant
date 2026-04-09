from .experiment import BehavioralExperiment
from .personalities import PersonalityFactory
from .comparison import PaperComparison

try:
    from .otree import OTreeExperiment
except ImportError:
    pass  # otree dependencies optional
