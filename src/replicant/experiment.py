"""
Experiment harness — run a game many times and summarize (DESIGN.md #3, #4).

A "cell" is one (game, persona, model) combination. run_cell repeats it N times
(each rep with a distinct but reproducible seed), extracts the behavioral metric
per rep via the game registry, and returns the distribution + summary stats +
the cited human baseline.

The persona is a plain string — this harness is decoupled from how it was built.
"""

import os

from .games import GAMES
from .stats import summarize
from .runners.otree import run_batch

SERVER = "http://localhost:8000"
REST_KEY = "test-rest-key"


def run_cell(game: str, persona: str, model: str, reps: int = 5,
             server: str = SERVER, api_key: str = None,
             temperature: float = 1.0, seed: int = None,
             rest_key: str = REST_KEY, runner=None,
             persona_label: str = "persona") -> dict:
    """Run one (game, persona, model) cell `reps` times and summarize.

    Args:
        game: key in games.GAMES.
        persona: system-prompt string (built by any persona method; "" = baseline).
        model: OpenRouter model id.
        reps: number of repetitions (the N in your stats).
        seed: base seed; rep i uses seed+i for reproducible-but-distinct draws.
        runner: callable(server, game, n, personas, model, rest_key, temperature,
            seed) -> results. Defaults to runners.otree.run_batch (injectable for tests).

    Returns dict with values (per-rep metric), summary, baseline, raw_runs.
    """
    if game not in GAMES:
        raise ValueError(f"Unknown game '{game}'. Known: {list(GAMES)}")
    spec = GAMES[game]
    runner = runner or run_batch

    values, raw_runs = [], []
    for i in range(reps):
        rep_seed = None if seed is None else seed + i
        results = runner(server, game, spec["n"], [persona] * spec["n"], model,
                         api_key=api_key, rest_key=rest_key,
                         temperature=temperature, seed=rep_seed)
        values.append(spec["extract"](results))
        raw_runs.append(results)

    return {
        "game": game,
        "model": model,
        "persona": persona_label,
        "reps": reps,
        "temperature": temperature,
        "seed": seed,
        "metric": spec["metric"],
        "label": spec["label"],
        "values": values,
        "summary": summarize(values),
        "baseline": spec["baseline"],
        "raw_runs": raw_runs,
    }


def run_experiment(name: str, cells_spec: list, model: str, reps: int = 5,
                   seed: int = None, temperature: float = 1.0,
                   server: str = SERVER, api_key: str = None, runner=None,
                   out_dir: str = None) -> dict:
    """Run several cells and (optionally) persist provenance + CSV + methods.

    Args:
        name: experiment name (used as the output subdir).
        cells_spec: list of (game, persona_string, persona_label) tuples.
        out_dir: if given, writes <out_dir>/<name>/{results.json, data.csv,
            methods.txt} — full provenance + raw transcripts, tidy CSV, and
            paper-ready sentences.

    Returns: {experiment, cells, cost_usd, [out_dir]}.
    """
    import json
    from .providers import openrouter
    from . import results as results_mod
    from . import report

    openrouter.reset_cost()
    cells = [
        run_cell(game, persona, model, reps=reps, server=server, api_key=api_key,
                 temperature=temperature, seed=seed, runner=runner,
                 persona_label=lbl)
        for (game, persona, lbl) in cells_spec
    ]
    cost = openrouter.get_cost()
    out = {"experiment": name, "cells": cells, "cost_usd": cost}

    if out_dir:
        exp_dir = os.path.join(out_dir, name)
        meta = results_mod.provenance(model, temperature, seed, cost_usd=cost,
                                      experiment=name, reps=reps)
        # results.json holds EVERYTHING — full per-agent transcripts (every
        # message seen + response, retries included), provenance, raw runs.
        results_mod.save(cells, meta, out_dir=exp_dir, run_id="results")
        report.export_csv(cells, os.path.join(exp_dir, "data.csv"))
        with open(os.path.join(exp_dir, "methods.txt"), "w") as f:
            f.write("\n".join(report.methods_section(c) for c in cells))
        out["out_dir"] = exp_dir

        # Append a one-line summary to a running index of every experiment.
        index = {
            **meta,
            "dir": exp_dir,
            "cells": [{"game": c["game"], "persona": c["persona"],
                       "metric": c["metric"], "summary": c["summary"],
                       "baseline": c["baseline"]["value"]} for c in cells],
        }
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "experiments.jsonl"), "a") as f:
            f.write(json.dumps(index, default=str) + "\n")

    return out
