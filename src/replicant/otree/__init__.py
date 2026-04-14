"""
oTree integration — run LLM agents as participants on a real oTree server.

LLM bots connect to a running oTree server as participants. oTree handles
rounds, groups, payoffs. Supports human-AI mixing — some participants are
humans, some are LLMs.

Usage:
    from replicant.otree import OTreeSession

    session = OTreeSession("http://localhost:8000", model="stepfun/step-3.5-flash")
    results = session.run("public_goods", n_bots=6)
"""

import os

from .parser import parse, OTreeApp, FieldDef, PageDef
from .client import OTreeClient, PageData, FormField
from .bot import LLMBot, FormController, run_bots
from .hybrid import HybridSession
from .export import OTreeExporter

from ..personalities import PersonalityFactory, build_description, POPULATION_NORMS
from ..personalities.factory import _score_to_weight, sample_personalities


# ── Server mode ─────────────────────────────────────────────────────

class OTreeSession:
    """
    Connect LLM agents to a running oTree server.

    The oTree server runs normally — same experiment, same web interface.
    LLM bots join as participants, read each page, make decisions via LLM,
    and submit. Humans can participate alongside bots in the same session.
    """

    def __init__(self, server_url: str, model: str = "stepfun/step-3.5-flash",
                 api_key: str = None):
        self.server_url = server_url.rstrip('/')
        self.model = model
        self.api_key = api_key or os.environ.get("OPEN_ROUTER_API_KEY", "")

    def run(self, session_config: str, n_bots: int = 6,
            personalities: list[str] | None = None,
            big5: bool = False,
            rest_key: str | None = None) -> list[dict]:
        """
        Create an oTree session and run LLM bots through it.

        Args:
            session_config: Name of the oTree session config (e.g. "ertan2009").
            n_bots: Number of LLM participants.
            personalities: optional list of personality description strings,
                one per bot. Use replicant.sample_personalities() to generate.
            big5: If True (and personalities is None), sample random Big Five
                personalities from population norms.
            rest_key: oTree REST API key (from settings.py OTREE_REST_KEY).

        Returns:
            List of result dicts, one per bot.
        """
        urls = OTreeClient.create_session(
            self.server_url, session_config, n_bots, rest_key,
        )
        return self.run_bots(urls, big5=big5, personalities=personalities)

    def run_bots(self, participant_urls: list[str],
                 big5: bool = False,
                 personalities: list[str] | None = None,
                 names: list[str] | None = None) -> list[dict]:
        """
        Run LLM bots for existing participant URLs.

        Use this for human-AI mixing: create a session with N participants,
        give some URLs to humans, and pass the rest here.
        """
        n = len(participant_urls)

        if personalities is None:
            if big5:
                personalities = sample_personalities(n=n)
            else:
                personalities = [""] * n

        print(f"\n{'='*55}", flush=True)
        print(f"oTree Session | {self.model} | {n} bots", flush=True)
        print(f"Server: {self.server_url}", flush=True)
        print(f"{'='*55}\n", flush=True)

        return run_bots(self.server_url, participant_urls, personalities,
                        self.model, self.api_key, names)

    def export_results(self, app_name: str = None, session_code: str = None,
                       output_dir: str = "results", rest_key: str = None) -> str:
        """
        Download experiment data from oTree as a CSV file.

        Args:
            app_name: oTree app name to export. If None, exports wide CSV.
            session_code: restrict to a specific session. If None, exports all.
            output_dir: directory to save the CSV
            rest_key: oTree REST API key (defaults to OTREE_REST_KEY env)

        Returns:
            Path to the saved CSV file.
        """
        exporter = OTreeExporter(self.server_url, rest_key=rest_key)
        if app_name:
            return exporter.export_app(app_name, output_dir=output_dir,
                                        session_code=session_code)
        return exporter.export_wide(output_dir=output_dir,
                                     session_code=session_code)


__all__ = [
    "OTreeSession", "HybridSession", "OTreeExporter",
    "parse", "OTreeApp", "FieldDef", "PageDef",
    "OTreeClient", "PageData", "FormField",
    "LLMBot", "FormController", "run_bots",
]
