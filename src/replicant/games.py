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
}
