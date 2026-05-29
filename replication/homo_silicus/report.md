# Homo Silicus — replication report

Step-by-step log of replicating Horton, Filippas & Manning (2023), *"Large
Language Models as Simulated Economic Agents: What Can We Learn from Homo
Silicus?"* ([arXiv:2301.07543](https://arxiv.org/abs/2301.07543)).

**Goal:** before integrating Horton's persona method into our own system,
replicate the paper one-to-one — their methods, their games, **no oTree** — and
confirm we get similar results. Only then change one variable at a time
(add oTree → swap model → …).

## Method (Phase 1)

- **No oTree.** Direct LLM prompts, exactly as in Horton's repo
  (`github.com/johnjosephhorton/homo_silicus`). Our only reuse is the OpenRouter
  call as transport; the prompt / persona / parsing logic is his, verbatim.
- **Model:** `openai/gpt-4o` (Horton's primary model in the updated paper),
  **temperature 0** (his setting). Using a Horton-class model isolates "is the
  replication correct?" before Phase 2 swaps in our own model.
- Scripts: `kkt.py`, `charness_rabin.py`.

## Experiment 1 — Kahneman, Knetsch & Thaler (1986) price fairness

A hardware store raises snow-shovel prices after a blizzard; rate it on a
4-point scale (1 Completely Fair … 4 Very Unfair). Persona = political ideology.
Prices {16, 20, 40, 100}.

**Result** (rating by persona × price):

| persona | $16 | $20 | $40 | $100 |
|---|---|---|---|---|
| (none) | 1 | 1 | 3 | 3 |
| socialist | 4 | 4 | 4 | 4 |
| leftist | 3 | 4 | 4 | 4 |
| liberal | 3 | 4 | 4 | 4 |
| moderate | 2 | 2 | 3 | 3 |
| libertarian | 2 | 2 | 2 | 2 |
| conservative | 2 | 2 | 2 | 2 |

- **Political gradient replicated:** left-leaning → unfair, right-leaning →
  acceptable. (Horton's Exp 1 finding.)
- **Dose-response replicated:** fairness falls as the price rises.
- *Note:* GPT-4o's no-persona baseline rates the $20 case "Fair," unlike the
  ~82% of humans (KKT 1986) who called it unfair — a model-default quirk to
  revisit in Phase 2 (Gemma's baseline was 80% unfair, closer to humans).

## Experiment 2 — Charness & Rabin (2002) allocation games + calibration

Person B chooses Left/Right across 6 allocation scenarios under each theory
persona (efficient / inequity-averse / self-interested / none).

**Persona behavior** (deterministic at temp 0):

| persona | Berk29 | Barc2 | Berk23 | Barc8 | Berk15 | Berk26 |
|---|---|---|---|---|---|---|
| none | R | R | L | R | R | R |
| inequity_averse | R | L | L | R | R | R |
| self_interested | R | L | L | L | L | L |
| efficient | R | R | L | R | R | R |

- `self_interested` picks the own-payoff-maximizing option wherever it pays more
  (Barc2/Barc8/Berk15/Berk26) — theory-consistent, as Horton reports.

**Calibration** (Horton Sec 2.2.1): fit a simplex mixture of the three theory
personas to the human "proportion chose Left" vector (Charness & Rabin 2002
game-by-game table: Berk29 .31, Barc2 .52, Berk23 1.00, Barc8 .67, Berk15 .27,
Berk26 .78).

| | efficient | inequity_averse | self_interested |
|---|---|---|---|
| **ours (GPT-4o)** | **44%** | **0%** | **56%** |
| Horton Claude-3.5 | 44% | 0% | 56% |
| Horton Deepseek | 44% | 0% | 56% |
| Horton GPT-4o | 37% | 10% | 53% |
| Horton Llama-3-70B | 49% | 0% | 51% |

**Our calibrated weights match Horton's reported weights** (identical to his
Claude-3.5 / Deepseek; same ballpark as GPT-4o / Llama). In-sample fit RMSE 0.20
— deliberately imperfect: with 6 targets and 3 weights the fit is
*overdetermined*, so it cannot memorize the data (the anti-overfitting property
the multi-game design buys you, unlike a single game).

## Phase 2 — change one variable at a time

Starting from the working Charness-Rabin replication, change exactly one thing
and check the calibrated weights stay in Horton's regime.
(`charness_rabin_otree.py`.)

| step | change | efficient | inequity | self | RMSE |
|---|---|---|---|---|---|
| Phase 1 | none (direct prompts, GPT-4o) | 44% | 0% | 56% | 0.20 |
| Phase 2a | **+ oTree** (GPT-4o) | 36% | 10% | 54% | 0.19 |
| Phase 2b | **+ oTree, model = Gemma** | 44% | 0% | 56% | 0.20 |

- **2a (add oTree):** weights stayed in regime; the page framing nudged
  `inequity_averse` on 2 scenarios, shifting 10% onto inequity — landing on
  Horton's *own* GPT-4o weights (37/10/53). oTree validated as transport.
- **2b (swap model to Gemma):** weights 44/0/56 — identical to Horton's
  Claude-3.5/Deepseek. The calibration replicates on our target model.

**Conclusion:** Horton's persona-conditioning + mixture-calibration result is
robust to (a) running through oTree and (b) using Gemma. We can build on it.

## Status

- [x] Phase 1 — replicate (KKT + Charness-Rabin), no oTree, results match paper.
- [x] Phase 2 — add oTree, then swap model to Gemma; weights stay in Horton's regime.
- [ ] Phase 4 — selectable persona-injection method.

Cost so far: ~$0.06 (GPT-4o for replication, Gemma for the model-swap step).
