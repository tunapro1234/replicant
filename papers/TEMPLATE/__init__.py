"""
TEMPLATE — paper replication scaffold.

Copy this directory and rename to start a new paper replication.
See README.md in this directory for instructions.
"""

from .config import (
    # Add your paper's exported config here, e.g.:
    # ENDOWMENT, GROUP_SIZE, MPCR, PAPER_FINDINGS,
)
from .experiment import build
from .analyze import analyze

__all__ = ["build", "analyze"]
