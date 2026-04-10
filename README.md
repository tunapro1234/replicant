# replicant

LLM-based replication framework for behavioral economics experiments.

Run classic econ experiments with LLM agents instead of humans. Validate that the personalities you assign actually stick. Compare your results to published findings. Plug into [oTree](https://www.otree.org/) to use real experiment platforms.

## What is this?

`replicant` is a Python toolkit for using large language models as simulated participants in behavioral economics experiments. It builds on [EDSL](https://github.com/expectedparrot/edsl) and provides:

- **BFI-2-Expanded personality induction** with cross-instrument validation (Mini-IPIP)
- **Multi-part experiment runner** with automatic retry and statistical analysis
- **oTree integration** — bots that connect to a real oTree server as participants
- **Paper replication tools** — compare simulated results to published findings

The first paper replicated is **Ertan, Page & Putterman (2009)** — *"Who to Punish? Individual Decisions and Majority Rule in Mitigating the Free Rider Problem"* (European Economic Review, 53(5), 495-511).

## Why "replicant"?

Two reasons. First, replication: the goal is to reproduce human behavioral findings with LLM agents. Second, the Blade Runner sense: synthetic agents that approximate but don't perfectly equal humans. Both meanings apply.

## Project Structure

```
src/
├── replicant/                            # The framework
│   ├── experiments/
│   │   ├── runner.py                     # BehavioralExperiment
│   │   ├── comparison.py                 # PaperComparison
│   │   └── templates/
│   │       └── public_goods.py           # Reusable VCM surveys
│   ├── personalities/
│   │   ├── factory.py                    # PersonalityFactory + sentence bank
│   │   └── validation.py                 # Mini-IPIP cross-instrument testing
│   ├── otree/
│   │   ├── client.py                     # HTTP client for oTree server
│   │   ├── bot.py                        # LLMBot + FormController
│   │   ├── parser.py                     # Parse oTree app source
│   │   └── translator.py                 # oTree → EDSL converter
│   └── analysis/                         # (reserved for future generic tools)
│
└── papers/                               # Paper-specific implementations
    └── ertan2009/
        ├── config.py                     # Game parameters + paper findings
        ├── experiment.py                 # Wires template to config
        ├── analyze.py                    # Paper-specific analysis
        ├── run.py                        # CLI entry point
        ├── compare.py                    # Default vs personality comparison
        ├── figures.py                    # Plot generation
        └── fig_personality.py            # Personality scatter plots

tests/
└── otree_server/                         # Real oTree server (Docker)
    ├── ertan2009/                        # Our experiment as an oTree app
    ├── dictator/, prisoner/, trust/, ...  # 12+ classic games
    └── Dockerfile

paper/                                    # The research paper
├── paper.tex
├── paper.pdf                              # 16 pages
└── figures/

results/                                  # Experiment outputs (CSV/JSON)
```

## Quick Start

### Prerequisites

- Python 3.10+
- An [OpenRouter](https://openrouter.ai) API key (for LLM access)
- [EDSL](https://github.com/expectedparrot/edsl) (`pip install edsl`)
- (Optional) Docker for the oTree server

### Setup

```bash
export OPEN_ROUTER_API_KEY="your-key-here"
```

### Run a paper replication

```bash
cd src

# Default: 50 agents, no personality
python -m papers.ertan2009.run -n 50

# With Big Five personalities sampled from population norms
python -m papers.ertan2009.run -n 50 --random-personalities --seed 42

# With named profiles (5 archetypes)
python -m papers.ertan2009.run -n 25 --big5

# Different model
python -m papers.ertan2009.run -n 50 --model deepseek/deepseek-v3.2
```

### Validate personality induction

```python
from replicant.personalities.validation import run_continuous_validation

results = run_continuous_validation(n=20, model="stepfun/step-3.5-flash")
# Reports Pearson r, R², MAE, bias per Big Five domain
```

## Two Pipelines

### Pipeline 1: EDSL (single-shot)

For fast, structured experiments without group interaction.

```python
from replicant import BehavioralExperiment, PersonalityFactory
from replicant.experiments.templates.public_goods import contribution_survey

factory = PersonalityFactory()
agents = factory.create_random_population(n=50, seed=42)

exp = BehavioralExperiment("my_experiment", model="stepfun/step-3.5-flash")
exp.add_part("baseline", contribution_survey(20, 5, 0.4))
results = exp.run(agents)
```

### Pipeline 2: oTree (multi-round, group-aware)

For realistic experiments with rounds, groups, and payoffs. LLM bots connect to a running oTree server as HTTP clients — same interface humans would use through a browser.

```bash
# Start the oTree server
docker compose up -d
```

```python
from replicant.otree import OTreeSession

session = OTreeSession("http://localhost:8000", model="stepfun/step-3.5-flash")
results = session.run("ertan2009", n_bots=5, big5=True)
```

The oTree server can also be used by humans alongside bots — useful for hybrid experiments.

## BFI-2 Personality System

`replicant` uses the **BFI-2-Expanded** format (Soto & John, 2017) — instead of giving LLMs numeric trait scores (which don't reliably influence behavior), it builds rich personality descriptions from a 7-level sentence bank.

```python
from replicant import PersonalityFactory

factory = PersonalityFactory()

# Sample from US adult population norms
agents = factory.create_random_population(n=50)

# Skewed population (e.g., all disagreeable)
agents = factory.create_random_population(
    n=50, mean_overrides={"agreeableness": 1.5}
)

# Named archetypes
agents = factory.create_profile("cooperative", n=10)
agents = factory.create_profile("selfish", n=10)
```

### Validation

We test that personality induction actually works using **cross-instrument validation**: assign with BFI-2-Expanded sentences, measure with the Mini-IPIP 20-item Likert scale (different wording so the model can't parrot the assignment).

| Profile | Match | r |
|---------|-------|---|
| Cooperative | 5/5 | — |
| Selfish | 4/5 | — |
| Leader | 5/5 | — |
| Anxious | 5/5 | — |
| Average | 3/5 | — |
| **Overall** | **22/25 (88%)** | **see continuous validation** |

## Adding a New Paper

1. Create `src/papers/<paper_name>/config.py` with game parameters and known findings
2. Create `src/papers/<paper_name>/experiment.py` wiring a template to the config
3. Create `src/papers/<paper_name>/run.py` as a CLI entry point
4. (Optional) Add an oTree app under `tests/otree_server/<paper_name>/`

## Known Models

| Model | Cost | Notes |
|-------|------|-------|
| `stepfun/step-3.5-flash` | $0.10 / $0.30 per M | Reasoning model, slow but thoughtful |
| `deepseek/deepseek-v3.2` | $0.26 / $0.38 per M | Fast non-reasoning model |
| `qwen/qwen3.6-plus:free` | Free | Often rate-limited |
| `meta-llama/llama-3.1-8b-instruct` | $0.02 / $0.05 per M | Cheapest option |

## Citation

If you use `replicant` in research, please cite the underlying tools:

```
EDSL: Horton, J. J., et al. (2024). Expected Parrot Domain-Specific Language.
oTree: Chen, D. L., Schonger, M., & Wickens, C. (2016). oTree—An open-source
       platform for laboratory, online, and field experiments.
```

## License

MIT
