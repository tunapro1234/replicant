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


def run_config(config: dict, api_key: str = None, runner=None,
               out_dir: str = None) -> dict:
    """Run a declarative experiment config and (optionally) persist everything.

    Config keys: model, reps, seed, temperature, server, experiment (name),
    and cells = [{game, persona: <spec>}, ...] where <spec> is a persona
    resolution spec (see personas/resolve.py).

    If out_dir is given, writes <out_dir>/<experiment>/{results.json, data.csv,
    methods.txt} with full provenance + raw transcripts + tidy CSV.
    """
    from .personas.resolve import resolve, label
    from .providers import openrouter
    from . import results as results_mod
    from . import report

    model = config["model"]
    reps = config.get("reps", 5)
    seed = config.get("seed")
    temperature = config.get("temperature", 1.0)
    server = config.get("server", SERVER)
    name = config.get("experiment", "experiment")

    openrouter.reset_cost()
    cells = []
    for cc in config["cells"]:
        pspec = cc["persona"]
        cell = run_cell(
            cc["game"], resolve(pspec), model, reps=reps, server=server,
            api_key=api_key, temperature=temperature, seed=seed,
            runner=runner, persona_label=label(pspec),
        )
        cells.append(cell)
    cost = openrouter.get_cost()

    out = {"experiment": name, "cells": cells, "cost_usd": cost}

    if out_dir:
        exp_dir = os.path.join(out_dir, name)
        meta = results_mod.provenance(model, temperature, seed, cost_usd=cost,
                                      experiment=name, reps=reps)
        results_mod.save(cells, meta, out_dir=exp_dir, run_id="results")
        report.export_csv(cells, os.path.join(exp_dir, "data.csv"))
        with open(os.path.join(exp_dir, "methods.txt"), "w") as f:
            f.write("\n".join(report.methods_section(c) for c in cells))
        out["out_dir"] = exp_dir

    return out


def main():
    import argparse
    import sys
    from . import config as config_mod
    from . import report

    parser = argparse.ArgumentParser(
        description="Run a declarative replicant experiment config.")
    parser.add_argument("config", help="path to .json/.yaml experiment config")
    parser.add_argument("--out-dir", default="results")
    args = parser.parse_args()

    if not os.environ.get("OPEN_ROUTER_API_KEY"):
        print("Set OPEN_ROUTER_API_KEY")
        sys.exit(1)

    cfg = config_mod.load(args.config)
    out = run_config(cfg, out_dir=args.out_dir)

    print(report.summary_table(out["cells"]))
    print(f"\nCost: ${out['cost_usd']:.4f}")
    if out.get("out_dir"):
        print(f"Saved to {out['out_dir']}/ (results.json, data.csv, methods.txt)")


if __name__ == "__main__":
    main()
