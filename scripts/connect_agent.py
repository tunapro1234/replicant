"""
Connect one LLM agent to a running oTree participant URL and play it through.

The oTree server can live anywhere — you only need a participant's start URL.
Run this on any machine that can reach that URL; the agent joins exactly like
a human would in a browser.

Usage:
    python scripts/connect_agent.py <participant_url>
    python scripts/connect_agent.py <url> --persona "You only care about your own pay-off"
    python scripts/connect_agent.py <url> --model google/gemma-4-31b-it --json
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from replicant import play


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("url", help="oTree participant start URL")
    p.add_argument("--persona", default="", help="persona system prompt (default: none)")
    p.add_argument("--model", default="google/gemma-4-31b-it")
    p.add_argument("--json", action="store_true", help="print the full log as JSON")
    args = p.parse_args()

    if not os.environ.get("OPEN_ROUTER_API_KEY"):
        sys.exit("Set OPEN_ROUTER_API_KEY")

    result = play(args.url, persona=args.persona, model=args.model)

    if args.json:
        print(json.dumps(result["log"], indent=2))
        return

    for entry in result["log"]:
        if "answers" in entry:
            print(f"{entry['page']}: {entry['answers']}")
        elif "error" in entry:
            print(f"{entry['page']}: ERROR — {entry['error']}")


if __name__ == "__main__":
    main()
