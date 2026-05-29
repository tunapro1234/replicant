"""
Output writing for the simulator: raw decisions -> tidy CSV, plus the running
experiment index.

No metrics or baselines here — computing offer%, comparing to Engel/KKT, etc.
is analysis (the researcher's own scripts reading these files), not the
simulator's job.
"""

import csv
import json
import os


def _decisions(run: list) -> dict:
    """One run_batch result -> {agent: {field: value}} of recorded answers."""
    out = {}
    for r in run:
        for entry in r.get("log", []):
            if "answers" in entry:
                out.setdefault(r["agent"], {}).update(entry["answers"])
    return out


def to_rows(cells: list) -> list:
    """Raw long format: one row per (cell, rep, agent, decided field).

    Universal across games — analysis pivots/filters this however it likes.
    """
    rows = []
    for c in cells:
        base_seed = c.get("seed")
        for rep, run in enumerate(c["raw_runs"]):
            for agent, fields in _decisions(run).items():
                for field, value in fields.items():
                    rows.append({
                        "game": c["game"],
                        "persona": c["persona"],
                        "model": c["model"],
                        "rep": rep,
                        "agent": agent,
                        "field": field,
                        "value": value,
                        "seed": None if base_seed is None else base_seed + rep,
                        "temperature": c.get("temperature"),
                    })
    return rows


def export_csv(cells: list, path: str) -> str:
    """Write raw decisions as tidy long-format CSV (one row per rep/agent/field)."""
    rows = to_rows(cells)
    fields = ["game", "persona", "model", "rep", "agent", "field", "value",
              "seed", "temperature"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return path


def list_experiments(out_dir: str = "results") -> list:
    """Read the running index of every experiment (results/experiments.jsonl)."""
    path = os.path.join(out_dir, "experiments.jsonl")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def print_experiments(out_dir: str = "results") -> None:
    """Print a compact history of every experiment run (what, not results)."""
    runs = list_experiments(out_dir)
    if not runs:
        print(f"No experiments logged in {out_dir}/experiments.jsonl")
        return
    print(f"{'when':<21}{'experiment':<24}{'game':<16}{'persona':<18}{'reps':<5}")
    print("-" * 84)
    for r in runs:
        when = str(r.get("timestamp", ""))[:19]
        for c in r.get("cells", []):
            print(f"{when:<21}{r.get('experiment', ''):<24}{c.get('game', ''):<16}"
                  f"{c.get('persona', ''):<18}{c.get('reps', ''):<5}")
