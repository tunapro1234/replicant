"""
Reporting (DESIGN.md #6, #8): tidy export for analysis tools, plus an
auto-generated methods-section sentence for the paper.

Operates on "cells" — the dicts returned by experiment.run_cell.
"""

import csv


def to_rows(cells: list[dict]) -> list[dict]:
    """Tidy long format: one row per rep. Drops straight into pandas/R."""
    rows = []
    for c in cells:
        b = c.get("baseline") or {}
        for i, v in enumerate(c["values"]):
            rows.append({
                "game": c["game"],
                "model": c["model"],
                "persona": c.get("persona", "persona"),
                "metric": c["metric"],
                "rep": i,
                "value": v,
                "temperature": c.get("temperature"),
                "seed": (None if c.get("seed") is None else c["seed"] + i),
                "baseline_value": b.get("value"),
                "baseline_source": b.get("source"),
            })
    return rows


def export_csv(cells: list[dict], path: str) -> str:
    """Write tidy long-format CSV (one row per rep). Returns the path."""
    rows = to_rows(cells)
    fields = ["game", "model", "persona", "metric", "rep", "value",
              "temperature", "seed", "baseline_value", "baseline_source"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return path


def methods_section(cell: dict) -> str:
    """Paper-ready provenance sentence for one cell."""
    s = cell["summary"]
    b = cell.get("baseline") or {}
    n_per_rep = "agents"
    seed_txt = "unseeded" if cell.get("seed") is None else f"seed {cell['seed']}+"
    mean = s.get("mean")
    if mean is None:
        return (f"{cell['reps']} reps of persona '{cell.get('persona')}' on "
                f"{cell['model']} ({cell['game']}) produced no usable metric.")
    ci = ""
    if s.get("ci95_low") is not None and s.get("sd") is not None:
        ci = f" (95% CI [{s['ci95_low']:.1f}, {s['ci95_high']:.1f}])"
    line = (
        f"Across {cell['reps']} repetitions, agents with persona "
        f"'{cell.get('persona')}' played {cell['game']} on {cell['model']} "
        f"(temperature={cell.get('temperature')}, {seed_txt}) via OpenRouter. "
        f"Mean {cell['metric']} = {mean:.1f}{ci}"
    )
    if b.get("value") is not None:
        line += (f", vs human baseline {b['value']}% "
                 f"({b.get('source', 'n/a')}).")
    else:
        line += "."
    return line


def summary_table(cells: list[dict]) -> str:
    """Human-readable console table of cells vs baselines."""
    lines = [f"{'game':<16}{'model':<28}{'persona':<20}{'mean':<18}{'human':<8}"]
    lines.append("-" * 90)
    for c in cells:
        s = c["summary"]
        mean = s.get("mean")
        if mean is None:
            mean_txt = "—"
        elif s.get("ci95_low") is not None and s.get("sd") is not None:
            mean_txt = f"{mean:.1f} [{s['ci95_low']:.0f},{s['ci95_high']:.0f}]"
        else:
            mean_txt = f"{mean:.1f}"
        b = (c.get("baseline") or {}).get("value")
        b_txt = f"{b}%" if b is not None else "—"
        model = c["model"].split("/")[-1][:26]
        lines.append(f"{c['game']:<16}{model:<28}{c.get('persona','?'):<20}"
                     f"{mean_txt:<18}{b_txt:<8}")
    return "\n".join(lines)
