"""Smoke tests: public modules import, and the layer contracts hold."""


def test_top_level():
    import replicant
    assert hasattr(replicant, "__version__")
    assert callable(replicant.play)
    assert callable(replicant.run_batch)


def test_runner_otree():
    from replicant.runners.otree import (
        play, run_batch, OTreeClient, PageData, FormField, OTreeExporter,
    )
    assert all(callable(f) for f in [play, run_batch])
    exporter = OTreeExporter("http://localhost:8000", rest_key="test")
    assert exporter.server_url == "http://localhost:8000"


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
    from replicant.personas.big5 import personallm, bfi2

    assert len(bfi2.ITEMS) == 60

    specs = big5.sample(n=3, seed=42)
    assert len(specs) == 3
    for s in specs:
        assert set(s) == {"E", "A", "C", "N", "O"}
        assert all(1.0 <= v <= 5.0 for v in s.values())
        # the contract: a spec feeds the persona unpacked
        prompt = personallm(**s)
        assert prompt.startswith("You are a character who is")


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
    # extractor pulls offer from a fake dictator run
    fake = [{"agent": "bot_1", "log": [{"answers": {"kept": 70}}]}]
    assert GAMES["dictator"]["extract"](fake) == 30.0
    assert "source" in GAMES["dictator"]["baseline"]


def test_experiment_run_cell_with_fake_runner():
    from replicant.experiment import run_cell
    # fake runner: bot_1 always keeps 60 -> offer 40
    def fake(server, game, n, personas, model, api_key=None, rest_key=None, temperature=1.0, seed=None):
        return [{"agent": "bot_1", "log": [{"answers": {"kept": 60}}]}]
    cell = run_cell("dictator", "", "fake-model", reps=3, runner=fake)
    assert cell["reps"] == 3
    assert cell["values"] == [40.0, 40.0, 40.0]
    assert cell["summary"]["mean"] == 40.0
    assert cell["baseline"]["value"] == 28.35


def test_report_csv_and_methods(tmp_path):
    from replicant.experiment import run_cell
    from replicant import report

    def fake(server, game, n, personas, model, api_key=None, rest_key=None, temperature=1.0, seed=None):
        return [{"agent": "bot_1", "log": [{"answers": {"kept": 60}}]}]

    cell = run_cell("dictator", "", "fake/model", reps=3, seed=42,
                    runner=fake, persona_label="selfish")

    rows = report.to_rows([cell])
    assert len(rows) == 3
    assert rows[0]["game"] == "dictator" and rows[0]["persona"] == "selfish"
    assert rows[0]["seed"] == 42 and rows[1]["seed"] == 43  # seed+i
    assert rows[0]["baseline_source"].startswith("Engel")

    path = report.export_csv([cell], str(tmp_path / "out.csv"))
    assert path.endswith(".csv")
    with open(path) as f:
        assert "game,model,persona" in f.read()

    sentence = report.methods_section(cell)
    assert "dictator" in sentence and "fake/model" in sentence
    assert "human baseline 28.35%" in sentence


def test_persona_resolve():
    from replicant.personas.resolve import resolve, label
    assert resolve({"family": "baseline"})
    assert resolve({"family": "economics", "key": "self_interested"}) == \
        "You only care about your own pay-off"
    assert resolve({"family": "big5", "spec": {"E": 4, "A": 1, "C": 3, "N": 4, "O": 3}}) \
        .startswith("You are a character who is")
    assert label({"family": "economics", "key": "self_interested"}) == "self_interested"
    assert label({"family": "big5", "spec": {"E": 4, "A": 1, "C": 3, "N": 4, "O": 3}}) \
        == "big5_E+A-C+N+O+"


def test_run_config_with_fake_runner(tmp_path):
    from replicant.experiment import run_config
    from replicant import config as config_mod

    cfg = config_mod.load("tests/configs/dictator_personas.json")
    assert cfg["experiment"] == "dictator_personas"
    assert len(cfg["cells"]) == 4

    def fake(server, game, n, personas, model, api_key=None, rest_key=None, temperature=1.0, seed=None):
        keep = 20 if "own pay-off" in personas[0] else 50
        return [{"agent": "bot_1", "log": [{"answers": {"kept": keep}}]}]

    out = run_config(cfg, runner=fake, out_dir=str(tmp_path))
    assert len(out["cells"]) == 4
    personas = {c["persona"] for c in out["cells"]}
    assert "self_interested" in personas and "baseline" in personas
    # selfish kept 20 -> offer 80; baseline kept 50 -> offer 50
    selfish = next(c for c in out["cells"] if c["persona"] == "self_interested")
    assert selfish["summary"]["mean"] == 80.0
    import os
    assert os.path.exists(os.path.join(str(tmp_path), "dictator_personas", "data.csv"))
    assert os.path.exists(os.path.join(str(tmp_path), "dictator_personas", "methods.txt"))


def test_provenance_and_save(tmp_path):
    from replicant.results import provenance, save
    meta = provenance("m", temperature=1.0, seed=7, cost_usd=0.01, persona="x")
    assert meta["model"] == "m" and meta["seed"] == 7
    assert "git_commit" in meta and "timestamp" in meta
    path = save([{"agent": "bot_1", "log": []}], meta, out_dir=str(tmp_path))
    assert path.endswith(".json")
    import json
    with open(path) as f:
        saved = json.load(f)
    assert saved["meta"]["persona"] == "x"
    assert saved["results"][0]["agent"] == "bot_1"
