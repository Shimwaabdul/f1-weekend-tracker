"""Command-line interface for the F1 weekend tracker."""

import argparse
import sys

from f1tracker.api import APIError, get_json
from f1tracker.formatting import format_results, format_standings
from f1tracker.next_race import fetch_next_race, format_next_race


def main(argv: list[str] | None = None) -> int:
    """Run the selected tracker command and return an exit status."""
    parser = argparse.ArgumentParser(description="F1 race weekend tracker (times in Africa/Kigali).")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("next", "results", "standings"):
        commands.add_parser(name, help=f"Show {name} information")
    args = parser.parse_args(argv)
    try:
        if args.command == "next":
            output = format_next_race(fetch_next_race())
        elif args.command == "results":
            output = format_results(get_json("current/last/results/1.json"))
        else:
            output = format_standings(get_json("current/driverStandings.json"))
        print(output)
        return 0
    except APIError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
