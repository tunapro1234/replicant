"""
Experiment harness — run a game many times and summarize (DESIGN.md #3, #4).

A "cell" is one (game, persona, model) combination. run_cell repeats it N times
(each rep with a distinct but reproducible seed), extracts the behavioral metric
per rep via the game registry, and returns the distribution + summary stats +
the cited human baseline.

The persona is a plain string — this harness is decoupled from how it was built.
"""

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
        results = runner(server, game, spec["n"], [persona] * spec["n"],
                         model, rest_key, temperature, rep_seed)
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
