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


def test_games_registry():
    from replicant.games import GAMES
    assert "dictator" in GAMES and GAMES["dictator"]["baseline"]["value"] == 28.35
    fake = [{"agent": "bot_1", "log": [{"answers": {"kept": 70}}]}]
    assert GAMES["dictator"]["extract"](fake) == 30.0
    assert "source" in GAMES["dictator"]["baseline"]


# A fake runner lets us test the harness end-to-end without any API calls.
def _fake_runner(server, game, n, personas, model,
                 api_key=None, rest_key=None, temperature=1.0, seed=None):
    keep = 20 if "own pay-off" in personas[0] else 50
    return [{"agent": "bot_1", "log": [{"answers": {"kept": keep}}]}]


def test_experiment_run_cell():
    from replicant.experiment import run_cell
    cell = run_cell("dictator", "", "fake-model", reps=3, runner=_fake_runner)
    assert cell["reps"] == 3
    assert cell["values"] == [50.0, 50.0, 50.0]   # baseline keeps 50 -> offer 50
    assert cell["summary"]["mean"] == 50.0
    assert cell["baseline"]["value"] == 28.35


def test_run_experiment_saves(tmp_path):
    from replicant.experiment import run_experiment
    cells_spec = [
        ("dictator", "", "baseline"),
        ("dictator", "You only care about your own pay-off", "selfish"),
    ]
    out = run_experiment("t", cells_spec, "fake/model", reps=2, seed=42,
                         runner=_fake_runner, out_dir=str(tmp_path))
    assert len(out["cells"]) == 2
    selfish = next(c for c in out["cells"] if c["persona"] == "selfish")
    assert selfish["summary"]["mean"] == 80.0   # keeps 20 -> offer 80
    import os
    assert os.path.exists(os.path.join(str(tmp_path), "t", "data.csv"))
    assert os.path.exists(os.path.join(str(tmp_path), "t", "methods.txt"))
    assert os.path.exists(os.path.join(str(tmp_path), "t", "results.json"))


def test_report_methods_sentence():
    from replicant.experiment import run_cell
    from replicant import report
    cell = run_cell("dictator", "", "fake/model", reps=3, seed=42,
                    runner=_fake_runner, persona_label="baseline")
    sentence = report.methods_section(cell)
    assert "dictator" in sentence and "human baseline 28.35%" in sentence


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
