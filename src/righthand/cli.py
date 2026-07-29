from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .browser import BrowserExecutor
from .recorder import record
from .skills import builtin_registry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="righthand", description="BlackMamba semantic computer-control assistant")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Execute a semantic browser command")
    run.add_argument("utterance", help='Natural command, e.g. "busca en pinterest western rosa"')
    run.add_argument("--approve", action="store_true", help="Explicitly approve irreversible steps")
    run.add_argument("--headless", action="store_true", help="Run browser without a visible window")

    learn = sub.add_parser("learn", help="Record one demonstrated browser flow")
    learn.add_argument("name", help="Semantic name, e.g. pinterest.visual_search")
    learn.add_argument("url", help="Starting URL")
    learn.add_argument("--output-dir", default="recordings")

    sub.add_parser("skills", help="List installed semantic skills")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "skills":
        for name in builtin_registry().names():
            print(name)
        return 0

    if args.command == "learn":
        destination = record(args.name, args.url, output_dir=Path(args.output_dir))
        print(f"Recorded demonstration: {destination}")
        print("Review it before promoting it to a trusted semantic skill.")
        return 0

    if args.command == "run":
        registry = builtin_registry()
        try:
            skill, params = registry.resolve(args.utterance)
        except LookupError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(f"RightHand -> {skill.name} {params}")
        BrowserExecutor(headless=args.headless).execute(skill, params, approved=args.approve)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
