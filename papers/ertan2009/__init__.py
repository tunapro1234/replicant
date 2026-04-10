"""
Ertan, Page & Putterman (2009) — replication.

"Who to Punish? Individual Decisions and Majority Rule in Mitigating
the Free Rider Problem". European Economic Review, 53(5), 495-511.
"""

from .config import (
    ENDOWMENT, GROUP_SIZE, MPCR, PUNISHMENT_RATIO,
    REGIMES, ACTIVE_REGIMES, PROFILES, PAPER_FINDINGS,
)
from .experiment import build
from .analyze import analyze, save_results

__all__ = [
    "build", "analyze", "save_results",
    "ENDOWMENT", "GROUP_SIZE", "MPCR", "PUNISHMENT_RATIO",
    "REGIMES", "ACTIVE_REGIMES", "PROFILES", "PAPER_FINDINGS",
]
