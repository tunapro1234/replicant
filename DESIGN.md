# Design principles

`replicant` is research software, not a normal app. Research software lives or
dies by whether someone else (a reviewer, a collaborator, future-you) can trust
and reproduce a result. These principles are the north star — every feature
should serve at least one.

Drawn from how mature research tools are built: Expected Parrot's EDSL,
Anthropic's `inspect-ai`, EleutherAI's `lm-eval-harness`, and PsyBORGS (the
framework behind Horton et al.'s *Homo Silicus*).

## 1. Provenance is sacred
Every result traces back to the exact inputs that produced it: code commit,
model id, temperature, seed, prompt text, persona, date, and cost. A result you
cannot reproduce is worthless — papers get retracted over this. We stamp run
metadata onto every saved result.

## 2. Raw data is never discarded
Persist the full transcript — every prompt sent, every raw LLM response, token
counts, timestamps — not just the parsed answer. You re-analyze later in ways
you didn't anticipate. Parsing is lossy; the raw response is ground truth.

## 3. N, not n=1
Report distributions with error bars (mean ± 95% CI, effect sizes), never a
single point estimate. LLMs are stochastic; one sample is noise. "What's your
N?" is the first question any reviewer asks.

## 4. Ground truth is built in and cited
Human baselines from meta-analyses live in the tool with their source and sample
size. Every LLM-vs-human comparison is documented at the point of comparison.

## 5. Experiments are data, not code
A declarative config defines a run (games × models × personas × reps × seed) so
a collaborator can read and change the experiment without touching Python.

## 6. Output drops into analysis tools
Tidy export — one row per observation — straight into pandas/R/Jupyter. Nobody
should re-analyze by reading JSON by hand.

## 7. Cost and budget are first-class
Estimate before, report actual after. Researchers run on grants with real
ceilings.

## 8. The tool writes your methods section
Auto-emit the paper-ready sentence: "N agents (persona X) played game Y on model
Z at temperature T, seed S, on DATE; mean M (95% CI ...) vs human baseline B
(source)."

## Architectural consequence

The layer split (`sampling → persona → runner → provider`) exists so that the
human→LLM-subject pivot is a new `provider`, not a rewrite. The persona output
contract is a plain string; the input contract is per-family. Keep it that way:
new methods plug in without disturbing what already works (Gall's law — a
working simple system evolved into a working complex one).
