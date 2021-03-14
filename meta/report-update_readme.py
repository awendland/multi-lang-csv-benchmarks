#!/usr/bin/env python
import argparse
import json
from pathlib import Path
import re
import sys
from lib import __repo__
from lib.benchmark_stats import analyze_results
from lib.templates import templates_env


parser = argparse.ArgumentParser(
    description="""\
Insert a table summarizing benchmark results into the README.md

The table will be inserted in between two comment lines:

```
<!-- report-start -->
<!-- report-end -->
```

This allows the README to be repeatedly updated.\
"""
)
parser.add_argument(
    "results_json",
    default="-",
    type=str,
    help="file containing the JSON formatted results from benchmark.py, or '-' for stdin",
)
parser.add_argument(
    "--readme",
    default=__repo__ / "README.md",
    type=lambda p: Path(p).resolve(),
    help="path of the README.md to update",
)
args = parser.parse_args()


results_file = (
    sys.stdin if args.results_json == "-" else open(Path(args.results_json).resolve())
)
results = json.load(results_file)


results_table_md = templates_env.get_template("README-table.md.jinja").render(
    analyzed_results=analyze_results(results)
)

readme_md = args.readme.read_text()
args.readme.write_text(
    re.sub(
        r"<!--\s*report-start\s*-->[\s\S]*?<!--\s*report-end\s*-->",
        f"""\
<!-- report-start -->
{results_table_md}
<!-- report-end -->\
""",
        readme_md,
        re.MULTILINE,
    )
)
