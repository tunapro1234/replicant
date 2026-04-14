"""
CLI for deploying LLM bots to an oTree experiment.

The researcher runs their oTree server as usual — nothing changes on
the server side. This tool connects LLM agents as participants.

Usage:

  # Create session and run bots
  python -m replicant.otree http://localhost:8000 public_goods -n 6

  # With Big Five personalities
  python -m replicant.otree http://localhost:8000 public_goods -n 10 --big5

  # Join an existing session
  python -m replicant.otree http://localhost:8000 --session-code abc12345 -n 3

  # Direct participant URLs (for human-AI mixing)
  python -m replicant.otree http://localhost:8000 --urls URL1 URL2 URL3

  # Different model
  python -m replicant.otree http://localhost:8000 public_goods -n 6 --model deepseek/deepseek-v3.2
"""

import argparse

from .client import OTreeClient
from .bot import run_bots
from ..personalities.factory import PersonalityFactory, sample_personalities


def main():
    parser = argparse.ArgumentParser(
        prog="replicant-otree",
        description="Deploy LLM bots to a running oTree experiment.",
    )
    parser.add_argument("server", help="oTree server URL (e.g. http://localhost:8000)")
    parser.add_argument("session_config", nargs="?",
                        help="oTree session config name (e.g. public_goods)")
    parser.add_argument("-n", "--bots", type=int, default=6,
                        help="Number of LLM bots (default: 6)")
    parser.add_argument("--model", default="stepfun/step-3.5-flash",
                        help="LLM model to use")
    parser.add_argument("--big5", action="store_true",
                        help="Use Big Five personality agents")
    parser.add_argument("--rest-key", help="oTree REST API key")
    parser.add_argument("--session-code",
                        help="Join an existing session by its code")
    parser.add_argument("--urls", nargs="+",
                        help="Direct participant URLs (for human-AI mixing)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show live progress")

    args = parser.parse_args()
    server = args.server.rstrip('/')

    # ── Get participant URLs ────────────────────────────────────────
    if args.urls:
        urls = args.urls
        print(f"Using {len(urls)} provided participant URLs")
    elif args.session_code:
        print(f"Fetching participants for session {args.session_code}...")
        all_urls = OTreeClient.get_session_urls(server, args.session_code)
        urls = all_urls[:args.bots]
        print(f"Found {len(all_urls)} participants, using {len(urls)} for bots")
    elif args.session_config:
        print(f"Creating session '{args.session_config}' with {args.bots} participants...")
        urls = OTreeClient.create_session(
            server, args.session_config, args.bots, args.rest_key,
        )
        print(f"Created {len(urls)} participant slots")
    else:
        parser.error("Provide a session_config name, --session-code, or --urls")
        return

    # ── Build personalities ─────────────────────────────────────────
    n = len(urls)
    if args.big5:
        personalities = sample_personalities(n=n, seed=42)
        print(f"Big Five personalities: {n} agents (random from population norms)")
    else:
        personalities = [""] * n

    # ── Run ─────────────────────────────────────────────────────────
    print(f"\nDeploying {n} LLM bots ({args.model})")
    print(f"Server: {server}")
    print("=" * 55)

    results = run_bots(server, urls, personalities, args.model,
                       verbose=args.verbose)

    # ── Report ──────────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("RESULTS")
    print("=" * 55)
    for r in results:
        name = r.get('agent', '?')
        if 'error' in r:
            print(f"  {name}: ERROR — {r['error']}")
        else:
            n_decisions = len(r.get('decisions', []))
            print(f"  {name}: {n_decisions} decisions")
            for d in r.get('decisions', []):
                page = d.get('page', '?')
                answers = d.get('answers', {})
                print(f"    {page}: {answers}")


if __name__ == "__main__":
    main()
