#!/usr/bin/env python
import argparse
import json
from pathlib import Path
import sys
from lib.benchmark_stats import analyze_results
from lib.templates import templates_env


parser = argparse.ArgumentParser(description="Generate HTML from the report")
parser.add_argument(
    "results_json",
    default="-",
    type=str,
    help="file containing the JSON formatted results from benchmark.py, or '-' for stdin",
)
parser.add_argument(
    "--output",
    default=None,
    type=lambda p: Path(p).resolve(),
    help="file to write generated output HTML to, defaults to stdout",
)
args = parser.parse_args()


results_file = (
    sys.stdin if args.results_json == "-" else open(Path(args.results_json).resolve())
)
results = json.load(results_file)

print(
    templates_env.get_template("report.html.jinja").render(
        analyzed_results=analyze_results(results),
        max_trials=max((len(trials) for k, trials in results.items())),
    )
)
