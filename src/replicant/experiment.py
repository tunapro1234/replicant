"""
Experiment harness — run agents through a game and record raw decisions.

The simulator's only job: put N LLM agents into a game, repeat, and save
EVERYTHING raw (every decision + full transcript). It computes no metrics and
knows no human baselines — that is the researcher's analysis, done afterward on
the saved data (see scripts/analyze_*.py). Adding a game touches no code here.

`n` (agents per session) comes from oTree's num_demo_participants — the caller
passes it in (run_game reads it from /api/session_configs).
"""

import os

from .runners.otree import run_batch

SERVER = "http://localhost:8000"
REST_KEY = "test-rest-key"


def run_cell(game: str, persona: str, model: str, n: int, reps: int = 1,
             server: str = SERVER, api_key: str = None,
             temperature: float = 1.0, seed: int = None,
             rest_key: str = REST_KEY, runner=None,
             persona_label: str = "persona") -> dict:
    """Run one (game, persona) cell `reps` times. Returns raw runs — no metric.

    seed: base seed; rep i uses seed+i for reproducible-but-distinct draws.
    runner: injectable (defaults to runners.otree.run_batch) for testing.
    """
    runner = runner or run_batch
    runs = []
    for i in range(reps):
        rep_seed = None if seed is None else seed + i
        runs.append(runner(server, game, n, [persona] * n, model,
                           api_key=api_key, rest_key=rest_key,
                           temperature=temperature, seed=rep_seed))
    return {
        "game": game, "model": model, "persona": persona_label,
        "n": n, "reps": reps, "temperature": temperature, "seed": seed,
        "raw_runs": runs,
    }


def run_experiment(name: str, cells_spec: list, model: str, n: int,
                   reps: int = 1, seed: int = None, temperature: float = 1.0,
                   server: str = SERVER, api_key: str = None, runner=None,
                   out_dir: str = None) -> dict:
    """Run cells and (optionally) save raw transcripts + raw CSV + provenance.

    cells_spec: list of (game, persona_string, persona_label).
    n: agents per session (oTree's num_demo_participants).

    Writes <out_dir>/<name>/: results.json (full transcripts + provenance) and
    data.csv (raw decisions, one row per rep/agent/field). No metrics, no
    baselines — analysis reads these files separately.
    """
    import json
    from .providers import openrouter
    from . import results as results_mod
    from . import report

    openrouter.reset_cost()
    cells = [
        run_cell(game, persona, model, n, reps=reps, server=server,
                 api_key=api_key, temperature=temperature, seed=seed,
                 runner=runner, persona_label=lbl)
        for (game, persona, lbl) in cells_spec
    ]
    cost = openrouter.get_cost()
    out = {"experiment": name, "cells": cells, "cost_usd": cost}

    if out_dir:
        exp_dir = os.path.join(out_dir, name)
        meta = results_mod.provenance(model, temperature, seed, cost_usd=cost,
                                      experiment=name, reps=reps)
        results_mod.save(cells, meta, out_dir=exp_dir, run_id="results")
        report.export_csv(cells, os.path.join(exp_dir, "data.csv"))
        out["out_dir"] = exp_dir

        index = {**meta, "dir": exp_dir,
                 "cells": [{"game": c["game"], "persona": c["persona"],
                            "n": c["n"], "reps": c["reps"]} for c in cells]}
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "experiments.jsonl"), "a") as f:
            f.write(json.dumps(index, default=str) + "\n")

    return out
