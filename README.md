# replicant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Run behavioral-economics experiments with **LLM agents as subjects**.

`replicant` connects large language models to real [oTree](https://www.otree.org/)
experiments — the same incentivized games used with human participants — and
gives each agent a *persona* drawn from the behavioral-science literature. The
goal: study how LLMs behave in economic games, and how closely that tracks
human behavior.

> Install as `pyreplicant`, import as `replicant` (like `pillow`/`PIL`).

## Architecture

Four layers. Three stack; the runner sits perpendicular.

```
sampling/   produce person-specs        (WHAT to generate — e.g. Big Five draws)
   │
persona/    spec → a person (a prompt)   (HOW to express it — methods from papers)
   │
runners/    execute the experiment       (oTree today; more backends later)
   │
providers/  talk to the LLM              (OpenRouter today; Ollama / agent harness later)
```

The contracts that make this compose:

- **Persona output is universal** — every persona returns a system-prompt `str`.
- **Persona input is per-family, not universal** — a `big5` persona takes
  `{E,A,C,N,O}`; an `economics` persona takes a theory category. A sampler pairs
  with one family. There is deliberately no cross-family persona interface.
- **The runner only needs `(persona_string, model)`** — it doesn't care how the
  persona was built, so swapping the persona method or the provider changes
  nothing downstream.

```
src/replicant/
├── providers/        openrouter.py
├── sampling/         big5.py            # Big Five population norms → specs
├── personas/
│   ├── baseline/                        # null persona
│   ├── big5/         bfi2.py            # BFI-2 trait bank (data)
│   │                 personallm_2305_02547/   # binary adjectives (arXiv:2305.02547)
│   ├── economics/    homo_silicus_2301_07543/ # theory one-liners (arXiv:2301.07543)
│   └── edsl/                            # Expected Parrot Agent as a persona builder
└── runners/
    └── otree/        run.py, client.py, export.py
```

Persona folders are tagged with the source paper's arXiv id, so the method and
its release date are visible at a glance. `personas/RESEARCH.md` indexes the
broader landscape of methods we may implement.

## Quickstart

```bash
# 1. start the bundled oTree server (dictator, trust, prisoner, public goods,
#    charness_rabin, kahneman_fairness, and more)
docker compose up -d

# 2. set your OpenRouter key
export OPEN_ROUTER_API_KEY=sk-or-...

# 3a. quick API demo: sample a population → personas → dictator game
python tests/run_experiment.py --n 6

# 3b. or run a full, reproducible experiment from a config file
python -m replicant.experiment tests/configs/dictator_personas.json
```

A config defines the whole experiment as data (DESIGN.md #5):

```json
{
  "experiment": "dictator_personas", "model": "google/gemma-4-31b-it",
  "reps": 5, "seed": 42, "temperature": 1.0,
  "cells": [
    {"game": "dictator", "persona": {"family": "baseline"}},
    {"game": "dictator", "persona": {"family": "economics", "key": "self_interested"}},
    {"game": "dictator", "persona": {"family": "big5", "spec": {"E":2,"A":1,"C":3,"N":4,"O":3}}}
  ]
}
```

Running it writes `results/<experiment>/`:

- **`results.json`** — full provenance (git commit, model, temp, seed, version,
  cost, date) + every raw transcript. Reproducible, never lossy.
- **`data.csv`** — tidy, one row per repetition → straight into pandas/R.
- **`methods.txt`** — paper-ready sentences:
  *"Across 5 repetitions, agents with persona 'self_interested' played dictator
  on google/gemma-4-31b-it (temperature=1.0, seed 42+) … Mean offer_pct = 0.0
  (95% CI […]), vs human baseline 28.35% (Engel (2011) meta-analysis)."*

Or drive it from Python — each cell is repeated N times and summarized with a
human baseline:

```python
from replicant.experiment import run_cell
cell = run_cell("dictator", persona="", model="google/gemma-4-31b-it", reps=5, seed=42)
print(cell["summary"])    # {n, mean, sd, sem, ci95_low, ci95_high}
print(cell["baseline"])   # {value: 28.35, source: "Engel (2011) ...", ...}
```

Or a single agent on any participant URL:

```python
from replicant import play
result = play(participant_url, persona="", model="google/gemma-4-31b-it")
```

## Persona methods implemented

| Family | Method | Source | Spec |
|---|---|---|---|
| baseline | null | — | none |
| big5 | PersonaLLM | [arXiv:2305.02547](https://arxiv.org/abs/2305.02547) | `{E,A,C,N,O}` |
| economics | Homo Silicus | [arXiv:2301.07543](https://arxiv.org/abs/2301.07543) | theory category |
| edsl | Expected Parrot Agent | [github](https://github.com/expectedparrot/edsl) | trait dict |

## Design

This is research software — built around reproducibility, provenance, raw-data
preservation, N-not-n=1 statistics, cited baselines, and tidy export. The
guiding principles are in [DESIGN.md](DESIGN.md).

## Notes

- **Provider:** all LLM calls go through [OpenRouter](https://openrouter.ai), so
  any model (Gemma, Qwen, GLM, Llama, GPT, Claude, …) works by changing one
  string.
- **EDSL persona** requires the `edsl` package, which currently needs Python
  3.12 (see the project `.venv`). It is lazily imported, so the rest of the repo
  runs without it.
- **Roadmap:** the provider layer is where LLM-as-subject research will plug in
  — an agentic harness (OpenClaw / Hermes-style) becomes another provider
  without touching the persona, sampling, or runner layers.

## Why "replicant"?

Replication — reproducing human behavioral findings with LLM agents. And the
Blade Runner sense — synthetic agents that approximate but don't perfectly equal
humans. Both apply.
