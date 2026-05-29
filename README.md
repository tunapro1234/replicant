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
│   ├── big5/         personallm_2305_02547/   # binary adjectives (arXiv:2305.02547)
│   └── economics/    homo_silicus_2301_07543/ # theory one-liners (arXiv:2301.07543)
├── games.py          # cited human baselines + metric extractors
├── stats.py          # mean / 95% CI over repetitions
├── experiment.py     # run_cell (repeat N times) + run_experiment (+ save)
├── results.py        # provenance stamp + raw transcript persistence
├── report.py         # tidy CSV + auto methods-section sentence
└── runners/
    └── otree/        run.py, client.py
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

# 3. run the demo experiment: a few personas through the dictator game,
#    each repeated N times, mean +/- 95% CI vs the cited human baseline
python tests/run_experiment.py --reps 5
```

### Entry scripts (`scripts/`)

```bash
# Pick a game interactively; it auto-sizes the agent count and runs full-LLM.
# Self-contained — starts the local oTree server if it isn't already up.
python scripts/run_game.py
python scripts/run_game.py --game dictator        # skip the menu

# Connect one agent to ANY oTree participant URL (server can be anywhere).
python scripts/connect_agent.py <participant_url>
python scripts/connect_agent.py <url> --persona "You only care about your own pay-off"
```

The bundled oTree apps live in `otree_server/` (top level). Adding or editing a
game requires a rebuild — `docker compose up -d --build` — because the apps are
copied into the image.

This writes `results/dictator_demo/`:

- **`results.json`** — full provenance (git commit, model, temp, seed, version,
  cost, date) + every raw transcript. Reproducible, never lossy.
- **`data.csv`** — tidy, one row per repetition → straight into pandas/R.
- **`methods.txt`** — paper-ready sentences:
  *"Across 5 repetitions, agents with persona 'self_interested' played dictator
  on google/gemma-4-31b-it (temperature=1.0, seed 42+) … Mean offer_pct = 0.0
  (95% CI […]), vs human baseline 28.35% (Engel (2011) meta-analysis)."*

Drive it from Python — each cell is repeated N times and summarized vs a human
baseline:

```python
from replicant.experiment import run_cell
cell = run_cell("dictator", persona="", model="google/gemma-4-31b-it", reps=5, seed=42)
print(cell["summary"])    # {n, mean, sd, sem, ci95_low, ci95_high}
print(cell["baseline"])   # {value: 28.35, source: "Engel (2011) ...", ...}
```

Build the persona however you like — a theory one-liner or a sampled trait spec:

```python
from replicant.sampling import big5
from replicant.personas.big5 import personallm
from replicant.personas.economics.homo_silicus_2301_07543 import ALLOCATION_PERSONAS

theory = ALLOCATION_PERSONAS["self_interested"]   # "You only care about your own pay-off"
spec   = big5.sample(n=1, seed=42)[0]             # {E,A,C,N,O} from population norms
sampled = personallm(**spec)                       # -> persona string
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

## Design

This is research software — built around reproducibility, provenance, raw-data
preservation, N-not-n=1 statistics, cited baselines, and tidy export. The
guiding principles are in [DESIGN.md](DESIGN.md).

## Notes

- **Provider:** all LLM calls go through [OpenRouter](https://openrouter.ai), so
  any model (Gemma, Qwen, GLM, Llama, GPT, Claude, …) works by changing one
  string.
- **Roadmap:** the provider layer is where LLM-as-subject research will plug in
  — an agentic harness (OpenClaw / Hermes-style) becomes another provider
  without touching the persona, sampling, or runner layers.

## Why "replicant"?

Replication — reproducing human behavioral findings with LLM agents. And the
Blade Runner sense — synthetic agents that approximate but don't perfectly equal
humans. Both apply.
