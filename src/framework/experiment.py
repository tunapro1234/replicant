"""
BehavioralExperiment — Multi-part experiment runner built on EDSL.

Runs each experiment part in a subprocess to avoid an EDSL bug where
sequential Survey.run() calls in the same process return NaN.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import pickle

from edsl import AgentList, Model


class BehavioralExperiment:
    """
    Usage:
        exp = BehavioralExperiment("ertan2009", model="qwen/qwen3.6-plus:free")
        exp.add_part("baseline", survey, scenarios)
        exp.add_part("voting", survey)
        results = exp.run(agents)
    """

    def __init__(self, name, model=None):
        self.name = name
        self.parts = []
        self.model = self._resolve_model(model)

    def _resolve_model(self, model):
        if model is None:
            return Model()
        if isinstance(model, str):
            return Model(model, service_name="open_router", max_tokens=100000)
        return model

    def add_part(self, name, survey, scenarios=None, description=""):
        self.parts.append({
            "name": name,
            "survey": survey,
            "scenarios": scenarios,
            "description": description,
        })

    def _run_part_subprocess(self, part, agents):
        """Run a single part in a subprocess, return pandas DataFrame."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Serialize inputs
            survey_path = os.path.join(tmpdir, "survey.pkl")
            agents_path = os.path.join(tmpdir, "agents.pkl")
            scenarios_path = os.path.join(tmpdir, "scenarios.pkl")
            output_path = os.path.join(tmpdir, "output.pkl")

            with open(survey_path, "wb") as f:
                pickle.dump(part["survey"], f)
            with open(agents_path, "wb") as f:
                pickle.dump(agents, f)
            if part["scenarios"] is not None:
                with open(scenarios_path, "wb") as f:
                    pickle.dump(part["scenarios"], f)

            model_name = self.model.model
            service = self.model.inference_service if hasattr(self.model, 'inference_service') else "open_router"

            script = f'''
import pickle, os, sys
os.environ["OPEN_ROUTER_API_KEY"] = os.environ.get("OPEN_ROUTER_API_KEY", "")
sys.path.insert(0, ".")

from edsl import Model, AgentList, ScenarioList, Survey

with open("{survey_path}", "rb") as f:
    survey = pickle.load(f)
with open("{agents_path}", "rb") as f:
    agents = pickle.load(f)

model = Model("{model_name}", service_name="open_router", max_tokens=100000)
job = survey.by(agents).by(model)

scenarios_path = "{scenarios_path}"
if os.path.exists(scenarios_path):
    with open(scenarios_path, "rb") as f:
        scenarios = pickle.load(f)
    if isinstance(scenarios, list):
        scenarios = ScenarioList(scenarios)
    job = job.by(scenarios)

results = job.run()
df = results.to_pandas()
with open("{output_path}", "wb") as f:
    pickle.dump(df, f)
'''
            result = subprocess.run(
                [sys.executable, "-u", "-c", script],
                capture_output=True,
                text=True,
                timeout=600,
                env=os.environ.copy(),
            )

            if result.returncode != 0:
                stderr = result.stderr[-1000:]
                raise RuntimeError(f"Part '{part['name']}' failed:\n{stderr}")

            with open(output_path, "rb") as f:
                return pickle.load(f)

    def run(self, agents):
        """Run all parts, each in a subprocess. Returns dict of {part_name: DataFrame}."""
        if isinstance(agents, list):
            agents = AgentList(agents)

        total = len(self.parts)

        print(f"\n{'='*55}", flush=True)
        print(f"{self.name} | {self.model.model} | {len(agents)} agents", flush=True)
        print(f"{'='*55}", flush=True)

        results = {}
        for idx, part in enumerate(self.parts, 1):
            label = part["name"]
            if part["description"]:
                label += f" ({part['description']})"
            print(f"[{idx}/{total}] {label}...", flush=True)

            t0 = time.time()
            df = self._run_part_subprocess(part, agents)

            # Validate
            ans_cols = [c for c in df.columns if c.startswith("answer.")]
            if ans_cols:
                nan_pct = df[ans_cols].isna().all(axis=1).mean()
                if nan_pct > 0.5:
                    print(f"  WARNING: {nan_pct:.0%} NaN!", flush=True)
                else:
                    print(f"  OK ({len(df)} rows)", flush=True)

            results[part["name"]] = df
            print(f"  {time.time()-t0:.1f}s", flush=True)

        return results

    def run_multi_model(self, agents, models):
        """Run the full experiment once per model."""
        all_results = {}
        for m in models:
            name = m if isinstance(m, str) else m.model
            print(f"\n{'#'*55}", flush=True)
            print(f"Model: {name}", flush=True)
            print(f"{'#'*55}", flush=True)

            sub = BehavioralExperiment(self.name, model=m)
            sub.parts = self.parts
            all_results[name] = sub.run(agents)

        return all_results
