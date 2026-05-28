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

# 3. run the end-to-end demo: sample a population → personas → dictator game
python tests/run_experiment.py --n 6
```

In code:

```python
from replicant.sampling import big5
from replicant.personas.big5 import personallm
from replicant.runners.otree import run_batch

specs    = big5.sample(n=6, seed=42)           # [{E,A,C,N,O}, ...] on 1-5
personas = [personallm(**s) for s in specs]    # spec → persona string
results  = run_batch("http://localhost:8000", "dictator", 6, personas,
                     "google/gemma-4-31b-it")
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
