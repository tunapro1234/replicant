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
