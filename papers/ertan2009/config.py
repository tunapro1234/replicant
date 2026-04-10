"""
Ertan, Page & Putterman (2009) — paper-specific parameters and findings.

"Who to Punish? Individual Decisions and Majority Rule in Mitigating the
Free Rider Problem". European Economic Review, 53(5), 495-511.
"""

# ── Game parameters ─────────────────────────────────────────────────

ENDOWMENT = 20
GROUP_SIZE = 5
MPCR = 0.4               # marginal per capita return
PUNISHMENT_RATIO = 3     # 1 token spent → 3 removed from target

# ── Punishment regimes ──────────────────────────────────────────────

REGIMES = {
    "no_punishment": "NO punishment allowed.",
    "punish_low_only": (
        "Members CAN punish below-average contributors only. "
        f"Cost: 1 token, removes {PUNISHMENT_RATIO} from target."
    ),
    "punish_high_only": (
        "Members CAN punish above-average contributors only. "
        f"Cost: 1 token, removes {PUNISHMENT_RATIO} from target."
    ),
    "unrestricted": (
        "Members CAN punish ANY member. "
        f"Cost: 1 token, removes {PUNISHMENT_RATIO} from target."
    ),
}

ACTIVE_REGIMES = {k: v for k, v in REGIMES.items() if k != "no_punishment"}

# ── Contribution profiles for punishment decisions ──────────────────

PROFILES = [
    {"name": "all_cooperate",  "others": "18, 17, 19, 16", "avg": 17.5},
    {"name": "mixed",          "others": "15, 5, 18, 2",   "avg": 10.0},
    {"name": "one_freerider",  "others": "17, 18, 16, 2",  "avg": 13.25},
]

# ── Known findings from the paper (for comparison) ──────────────────

PAPER_FINDINGS = {
    "vote_punish_low_pct":  (0.85, "% voting to allow punishing low contributors (late rounds)"),
    "vote_punish_high_pct": (0.00, "% voting to allow punishing high contributors"),
}
