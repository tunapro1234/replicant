"""Smoke tests: public modules import, and the layer contracts hold."""


def test_top_level():
    import replicant
    assert hasattr(replicant, "__version__")
    assert callable(replicant.play)
    assert callable(replicant.run_batch)


def test_runner_otree():
    from replicant.runners.otree import play, run_batch, OTreeClient, PageData, FormField
    assert all(callable(f) for f in [play, run_batch])
    c = OTreeClient("http://localhost:8000")
    assert c.server_url == "http://localhost:8000"


def test_providers():
    from replicant.providers import complete
    assert callable(complete)


def test_baseline_persona():
    from replicant.personas.baseline import build_prompt
    assert build_prompt()


def test_economics_persona():
    from replicant.personas.economics.homo_silicus_2301_07543 import (
        ALLOCATION_PERSONAS, build_prompt,
    )
    assert "self_interested" in ALLOCATION_PERSONAS
    assert build_prompt("self_interested") == "You only care about your own pay-off"


def test_big5_family_contract():
    """sampling.big5 produces specs that personas.big5 consume directly."""
    from replicant.sampling import big5
    from replicant.personas.big5 import personallm

    specs = big5.sample(n=3, seed=42)
    assert len(specs) == 3
    for s in specs:
        assert set(s) == {"E", "A", "C", "N", "O"}
        assert all(1.0 <= v <= 5.0 for v in s.values())
        # the contract: a spec feeds the persona unpacked
        assert personallm(**s).startswith("You are a character who is")


def test_big5_sampler_is_seeded():
    from replicant.sampling import big5
    assert big5.sample(n=2, seed=1) == big5.sample(n=2, seed=1)


def test_stats_summarize():
    from replicant.stats import summarize
    s = summarize([10, 20, 30, 40, 50])
    assert s["n"] == 5 and s["mean"] == 30
    assert s["ci95_low"] < 30 < s["ci95_high"]
    assert summarize([])["n"] == 0
    assert summarize([42])["mean"] == 42 and summarize([42])["sd"] is None


# A fake runner lets us test the harness end-to-end without any API calls.
def _fake_runner(server, game, n, personas, model,
                 api_key=None, rest_key=None, temperature=1.0, seed=None):
    keep = 20 if "own pay-off" in personas[0] else 50
    return [{"agent": "bot_1",
             "log": [{"answers": {"kept": keep}}],
             "messages": [{"role": "system", "content": "..."}]}]


def test_experiment_run_cell_is_raw():
    """run_cell records raw runs only — no metric, no summary, no baseline."""
    from replicant.experiment import run_cell
    cell = run_cell("dictator", "", "fake-model", n=2, reps=3, runner=_fake_runner)
    assert cell["reps"] == 3 and cell["n"] == 2
    assert len(cell["raw_runs"]) == 3
    assert "summary" not in cell and "baseline" not in cell and "metric" not in cell
    # the raw decision is recoverable
    assert cell["raw_runs"][0][0]["log"][0]["answers"]["kept"] == 50


def test_run_experiment_saves_raw(tmp_path):
    import csv
    import os
    from replicant.experiment import run_experiment
    cells_spec = [
        ("dictator", "", "baseline"),
        ("dictator", "You only care about your own pay-off", "selfish"),
    ]
    out = run_experiment("t", cells_spec, "fake/model", n=2, reps=2, seed=42,
                         runner=_fake_runner, out_dir=str(tmp_path))
    assert len(out["cells"]) == 2
    assert os.path.exists(os.path.join(str(tmp_path), "t", "results.json"))
    assert os.path.exists(os.path.join(str(tmp_path), "experiments.jsonl"))
    # data.csv is RAW long format: rows of (persona, field=kept, value)
    with open(os.path.join(str(tmp_path), "t", "data.csv")) as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["field"] == "kept"            # raw field, not a computed metric
    selfish = [r for r in rows if r["persona"] == "selfish"]
    assert all(r["value"] == "20" for r in selfish)   # raw kept, not offer%


def test_experiment_index(tmp_path):
    from replicant.experiment import run_experiment
    from replicant import report
    run_experiment("a", [("dictator", "", "baseline")], "m", n=2, reps=2,
                   runner=_fake_runner, out_dir=str(tmp_path))
    run_experiment("b", [("dictator", "", "baseline")], "m", n=2, reps=2,
                   runner=_fake_runner, out_dir=str(tmp_path))
    runs = report.list_experiments(str(tmp_path))
    assert len(runs) == 2                       # index accumulates every run
    assert {r["experiment"] for r in runs} == {"a", "b"}
    # index records WHAT ran, not results (no metric/baseline)
    assert runs[0]["cells"][0]["game"] == "dictator"
    assert "summary" not in runs[0]["cells"][0]


def test_calibrate_mixture():
    from replicant.personas.economics.homo_silicus_2301_07543.calibrate import (
        fit_weights, population,
    )
    # Gemma case: selfish gives 0, fair gives 50; human mean 28.35.
    w, sse = fit_weights({"selfish": 0, "fair": 50}, 28.35)
    assert abs(w["fair"] - 0.57) < 0.02 and abs(w["selfish"] - 0.43) < 0.02
    assert sse < 0.5
    # weighted mean reproduces the target
    assert abs(w["fair"] * 50 + w["selfish"] * 0 - 28.35) < 1.0
    # population rounding sums to n
    counts = population(w, 100)
    assert sum(counts.values()) == 100


def test_provenance_and_save(tmp_path):
    from replicant.results import provenance, save
    meta = provenance("m", temperature=1.0, seed=7, cost_usd=0.01, persona="x")
    assert meta["model"] == "m" and meta["seed"] == 7
    assert "git_commit" in meta and "timestamp" in meta
    path = save([{"agent": "bot_1", "log": []}], meta, out_dir=str(tmp_path))
    import json
    with open(path) as f:
        saved = json.load(f)
    assert saved["meta"]["persona"] == "x"
