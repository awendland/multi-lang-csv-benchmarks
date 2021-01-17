import argparse
import json
from pathlib import Path
import statistics
import sys


parser = argparse.ArgumentParser(description="Execute CSV processing benchmarks")
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


rows = []
for benchmark, trials in results.items():
    done_lines_per_sec = [
        float(trial["done:lines"]) / float(trial["done:duration"]) * 1000
        for trial in trials
        if trial["status"] == "DONE"
    ]
    timeout_lines_per_sec = [
        float(trial["timeout:lines"]) / float(trial["timeout:time"]) * 1000
        for trial in trials
        if trial["status"] == "FAILED" and trial["failed:reason"] == "TIMEOUT"
    ]
    lines_per_sec = sorted(done_lines_per_sec + timeout_lines_per_sec)

    trial_cols = []
    for trial in trials:
        if trial["status"] == "DONE":
            trial_cols.append(str(trial["done:duration"]))
        elif trial["status"] == "FAILED":
            if trial["failed:reason"] == "TIMEOUT":
                trial_cols.append(
                    "TIMEOUT[lines={},time={}]".format(
                        trial["timeout:lines"], trial["timeout:time"]
                    )
                )
            else:
                trial_cols.append(trial["failed:reason"])
        else:
            trial_cols.append(trial["status"])

    rows.append(
        """\
    <tr>
        <td>
            <details>
                <summary>{name}</summary>
                <pre>{environment}</pre>
            </details
        </td>
        <td>{median:0.0f}</td>
        <td>{n_done}+{n_timeout}</td>
        {trial_cols}
    </tr>""".format(
            name=benchmark,
            environment=trials[0]["environment"],
            median=statistics.median(lines_per_sec),
            min=min(lines_per_sec),
            max=max(lines_per_sec),
            n_done=len(done_lines_per_sec),
            n_timeout=len(timeout_lines_per_sec),
            trial_cols="".join(["<td>{}</td>".format(c) for c in trial_cols]),
        )
    )


results_table = """\
<table>
    <thead>
        <tr>
            <th>Benchmark</th>
            <th>Median (lines / sec)</th>
            <th>N</th>
            {trial_headers}
        </tr>
    </thead>
    <tbody>
        {rows}
    </tbody>
</table>\
""".format(
    trial_headers="".join(
        [
            "<th>Trial #{} (ms)<th>".format(i)
            for i in range(len(next(iter(results.values()))))
        ]
    ),
    rows="\n        ".join(rows),
)


html = """\
<!DOCTYPE html>
<html>
<head>
</head>
<body>
{results_table}
</body>
</html>
""".format(
    results_table=results_table
)


print(html)
