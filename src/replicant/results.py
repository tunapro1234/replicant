"""
Result persistence + provenance (DESIGN.md #1, #2).

Every saved run carries the metadata needed to reproduce it (code commit,
model, temperature, seed, version, date, cost) and the full raw transcript
(every prompt + raw LLM response, via the runner's per-agent log). A result
you cannot trace is worthless.
"""

import json
import os
import subprocess
from datetime import datetime, timezone


def git_commit() -> str:
    """Short git commit hash of the working tree, or 'unknown'."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def provenance(model: str, temperature: float = None, seed: int = None,
               cost_usd: float = None, **extra) -> dict:
    """Build a provenance record for a run."""
    from . import __version__
    rec = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "replicant_version": __version__,
        "model": model,
        "temperature": temperature,
        "seed": seed,
        "cost_usd": cost_usd,
    }
    rec.update(extra)
    return rec


def save(results, meta: dict, out_dir: str = "results", run_id: str = None) -> str:
    """Persist a run (raw transcripts + provenance) to out_dir/<run_id>.json.

    Args:
        results: the runner output (list of per-agent dicts, with full logs).
        meta: provenance dict (see provenance()).
        out_dir: directory to write into.
        run_id: filename stem; defaults to a UTC timestamp.

    Returns: path to the written file.
    """
    os.makedirs(out_dir, exist_ok=True)
    if run_id is None:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(out_dir, f"{run_id}.json")
    with open(path, "w") as f:
        json.dump({"meta": meta, "results": results}, f, indent=2, default=str)
    return path
