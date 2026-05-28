"""
Game registry — one place that knows, per oTree game: how many players, how to
extract the behavioral metric from a run, and the human baseline with its
citation (DESIGN.md #4).

Baselines are meta-analytic means. Every comparison the tool makes is therefore
documented at the point of comparison — no magic numbers.
"""


def _decisions(results: list[dict]) -> dict:
    """Collapse runner output to {agent: {field: value}} of last answers."""
    out = {}
    for r in results:
        for entry in r.get("log", []):
            if "answers" in entry:
                out.setdefault(r["agent"], {}).update(entry["answers"])
    return out


def _dictator(results):
    d = _decisions(results)
    kept = d.get("bot_1", {}).get("kept")
    return None if kept is None else 100 - float(kept)


def _prisoner(results):
    d = _decisions(results)
    choices = []
    for v in d.values():
        c = v.get("cooperate")
        if c is not None:
            choices.append(str(c).lower() in ("true", "1", "cooperate"))
    return 100 * sum(choices) / len(choices) if choices else None


def _trust_sent(results):
    d = _decisions(results)
    sent = d.get("bot_1", {}).get("sent_amount")
    return None if sent is None else float(sent) / 10 * 100


def _public_goods(results):
    d = _decisions(results)
    c = [float(v["contribution"]) for v in d.values() if v.get("contribution") is not None]
    return sum(c) / len(c) if c else None


def _kahneman_unfair(results):
    d = _decisions(results)
    ratings = [int(v["fairness"]) for v in d.values() if v.get("fairness") is not None]
    if not ratings:
        return None
    return 100 * sum(1 for r in ratings if r >= 3) / len(ratings)  # 3,4 = (very) unfair


GAMES = {
    "dictator": {
        "n": 2,
        "metric": "offer_pct",
        "label": "Mean offer (% of pie given to receiver)",
        "extract": _dictator,
        "baseline": {
            "value": 28.35,
            "source": "Engel (2011) meta-analysis",
            "n_studies": 131, "n_obs": 41433,
        },
    },
    "prisoner": {
        "n": 2,
        "metric": "cooperation_rate",
        "label": "Cooperation rate (%)",
        "extract": _prisoner,
        "baseline": {
            "value": 47.0,
            "source": "Sally (1995) meta-analysis",
            "n_studies": 130, "n_obs": 30000,
        },
    },
    "trust": {
        "n": 2,
        "metric": "sent_pct",
        "label": "Amount sent by trustor (% of endowment)",
        "extract": _trust_sent,
        "baseline": {
            "value": 50.0,
            "source": "Johnson & Mislin (2011) meta-analysis",
            "n_studies": 162, "n_obs": 23000,
        },
    },
    "public_goods": {
        "n": 3,
        "metric": "contribution_pct",
        "label": "Mean contribution (% of endowment), round 1",
        "extract": _public_goods,
        "baseline": {
            "value": 50.0,
            "source": "Zelmer (2003) meta-analysis (round-1 contributions 40-60%)",
            "n_studies": 27, "n_obs": 10000,
        },
    },
    "kahneman_fairness": {
        "n": 1,
        "metric": "pct_unfair",
        "label": "% rating the price increase (very) unfair",
        "extract": _kahneman_unfair,
        "baseline": {
            "value": 82.0,
            "source": "Kahneman, Knetsch & Thaler (1986)",
            "n_studies": 1, "n_obs": 107,
        },
    },
}
