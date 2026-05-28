"""Smoke tests: public modules import without errors and expose their API."""


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
    assert exporter.rest_key == "test"


def test_providers():
    from replicant.providers import complete
    assert callable(complete)


def test_personas():
    from replicant.personas.baseline import build_prompt as baseline
    from replicant.personas.economics.homo_silicus_2301_07543 import (
        ALLOCATION_PERSONAS, build_prompt as homo_silicus,
    )
    assert "self_interested" in ALLOCATION_PERSONAS
    assert baseline()
    assert homo_silicus("self_interested") == "You only care about your own pay-off"


def test_bfi2_bank():
    from replicant.personas.big5 import bfi2
    assert len(bfi2.ITEMS) == 60
    assert set(bfi2.DOMAINS) == {"E", "A", "C", "N", "O"}
