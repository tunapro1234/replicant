# Paper Template

Copy this directory to create a new paper replication:

```bash
cp -r papers/TEMPLATE papers/your_paper_name
cd papers/your_paper_name
```

Then edit the files in this order:

1. **`config.py`** — Game parameters and known findings from the paper
2. **`experiment.py`** — Wire a template (or write your own survey) with the config
3. **`analyze.py`** — Paper-specific analysis: what to extract, how to compare
4. **`run.py`** — CLI entry point (usually no changes needed)

## File overview

```
your_paper/
├── __init__.py              # Package exports
├── config.py                # Game parameters + paper findings
├── experiment.py            # build() function returning BehavioralExperiment
├── analyze.py               # analyze() function
├── run.py                   # CLI: python -m papers.your_paper.run
├── results/                 # CSV/JSON output (gitignored)
└── replicated/              # Your paper write-up
    ├── paper.tex
    └── figures/
```

## Run it

From the project root:

```bash
python -m papers.your_paper.run -n 50 --random-personalities
```
