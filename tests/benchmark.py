"""
Benchmark: run all games × models × personas, compare against human data.

Usage:
    python tests/benchmark.py
    python tests/benchmark.py --games dictator prisoner
    python tests/benchmark.py --models google/gemma-4-31b-it
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from replicant.runners.otree import run_batch
from replicant.providers import openrouter

SERVER = "http://localhost:8000"
REST_KEY = "test-rest-key"

HUMAN = {
    "dictator":     {"metric": "mean_offer_pct", "human": 28.35, "label": "Mean offer %"},
    "prisoner":     {"metric": "cooperation_rate", "human": 47.0, "label": "Cooperation rate %"},
    "trust":        {"metric": "mean_sent_pct", "human": 50.0, "label": "Mean sent %"},
    "public_goods": {"metric": "mean_contribution_pct", "human": 50.0, "label": "Mean contribution %"},
}

GAMES = {
    "dictator":     {"n": 2},
    "prisoner":     {"n": 2},
    "trust":        {"n": 2},
    "public_goods": {"n": 3},
}

MODELS = [
    "google/gemma-4-31b-it",
    "meta-llama/llama-3-8b-instruct",
    "mistralai/mistral-small-3.2-24b-instruct",
    "microsoft/phi-4-mini-instruct",
    "minimax/minimax-m2.5:free",
    "z-ai/glm-4.7-flash",
]

PERSONAS = {
    "baseline": "",
}


def extract_metric(game, results):
    decisions = {}
    for r in results:
        for entry in r.get("log", []):
            if "answers" in entry:
                decisions[r["agent"]] = entry["answers"]

    if game == "dictator":
        kept = decisions.get("bot_1", {}).get("kept")
        if kept is not None:
            return {"mean_offer_pct": 100 - float(kept), "raw": decisions}

    elif game == "prisoner":
        choices = []
        for agent in ["bot_1", "bot_2"]:
            val = decisions.get(agent, {}).get("cooperate")
            if val is not None:
                choices.append(str(val).lower() in ("true", "1", "cooperate"))
        if choices:
            return {"cooperation_rate": 100 * sum(choices) / len(choices), "raw": decisions}

    elif game == "trust":
        sent = decisions.get("bot_1", {}).get("sent_amount")
        sent_back = decisions.get("bot_2", {}).get("sent_back_amount")
        out = {"raw": decisions}
        if sent is not None:
            out["mean_sent_pct"] = float(sent) / 10 * 100
        if sent_back is not None and sent is not None and float(sent) > 0:
            out["mean_returned_pct"] = float(sent_back) / (float(sent) * 3) * 100
        return out

    elif game == "public_goods":
        contribs = []
        for agent in decisions:
            c = decisions[agent].get("contribution")
            if c is not None:
                contribs.append(float(c))
        if contribs:
            return {"mean_contribution_pct": sum(contribs) / len(contribs), "raw": decisions}

    return {"raw": decisions}


CACHE_DIR = os.path.join(os.path.dirname(__file__), "benchmark_cache")


def _cache_key(game, model, persona_name):
    key = f"{game}|{model}|{persona_name}"
    return hashlib.md5(key.encode()).hexdigest()


def _cache_get(game, model, persona_name):
    path = os.path.join(CACHE_DIR, f"{_cache_key(game, model, persona_name)}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def _cache_set(game, model, persona_name, entry):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, f"{_cache_key(game, model, persona_name)}.json")
    with open(path, "w") as f:
        json.dump(entry, f, indent=2, default=str)


def run_benchmark(games, models, personas, api_key, no_cache=False):
    results = []

    for game in games:
        n = GAMES[game]["n"]
        for model in models:
            for persona_name, persona_text in personas.items():
                cached = None if no_cache else _cache_get(game, model, persona_name)
                if cached:
                    print(f"\n--- {game} | {model} | {persona_name} --- (cached)")
                    results.append(cached)
                    h = HUMAN.get(game, {})
                    metric_key = h.get("metric")
                    if metric_key and metric_key in cached.get("metrics", {}):
                        val = cached["metrics"][metric_key]
                        print(f"  {h['label']}: {val:.1f}% (human: {h['human']}%)")
                    continue

                print(f"\n--- {game} | {model} | {persona_name} ---")
                try:
                    raw = run_batch(SERVER, game, n,
                                   [persona_text] * n, model, api_key, REST_KEY)
                    metrics = extract_metric(game, raw)
                    entry = {
                        "game": game,
                        "model": model,
                        "persona": persona_name,
                        "metrics": metrics,
                    }
                    results.append(entry)
                    _cache_set(game, model, persona_name, entry)

                    h = HUMAN.get(game, {})
                    metric_key = h.get("metric")
                    if metric_key and metric_key in metrics:
                        val = metrics[metric_key]
                        print(f"  {h['label']}: {val:.1f}% (human: {h['human']}%)")
                    else:
                        print(f"  {metrics.get('raw', {})}")

                except Exception as e:
                    print(f"  ERROR: {e}")
                    results.append({
                        "game": game, "model": model,
                        "persona": persona_name, "error": str(e),
                    })

    return results


def print_summary(results):
    print("\n" + "=" * 70)
    print(f"{'Game':<15} {'Model':<30} {'Persona':<12} {'Result':<12} {'Human':<8}")
    print("=" * 70)

    for r in results:
        if "error" in r:
            print(f"{r['game']:<15} {r['model']:<30} {r['persona']:<12} {'ERROR':<12}")
            continue

        game = r["game"]
        h = HUMAN.get(game, {})
        metric_key = h.get("metric")
        val = r["metrics"].get(metric_key, "—") if metric_key else "—"
        human = h.get("human", "—")

        val_str = f"{val:.1f}%" if isinstance(val, (int, float)) else str(val)
        human_str = f"{human}%" if isinstance(human, (int, float)) else str(human)

        print(f"{game:<15} {r['model']:<30} {r['persona']:<12} {val_str:<12} {human_str:<8}")

    print("=" * 70)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", nargs="+", default=list(GAMES.keys()))
    parser.add_argument("--models", nargs="+", default=MODELS)
    parser.add_argument("--output", default="tests/benchmark_results.json")
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("OPEN_ROUTER_API_KEY", "")
    if not api_key:
        print("Set OPEN_ROUTER_API_KEY")
        sys.exit(1)

    openrouter.reset_cost()
    results = run_benchmark(args.games, args.models, PERSONAS, api_key, no_cache=args.no_cache)
    cost = openrouter.get_cost()

    print_summary(results)
    print(f"\nTotal cost: ${cost:.4f}")

    out = {"timestamp": datetime.now().isoformat(), "cost_usd": cost, "results": results}
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
