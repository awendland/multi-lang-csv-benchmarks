from typing import Any, TypedDict
import statistics
from collections import OrderedDict

BenchmarkTrial = dict[str, Any]
BenchmarkResults = dict[str, list[BenchmarkTrial]]


class BenchmarkAnalysis(TypedDict):
    lps_unsorted: list[float]
    lps_done: list[float]
    lps_timeout: list[float]
    lps_stats_median: float
    trials: list[BenchmarkTrial]


def analyze_results(results: BenchmarkResults):
    analyzed_results: dict[str, BenchmarkAnalysis] = OrderedDict()

    for benchmark in sorted(results.keys()):
        trials = results[benchmark]
        analysis = {"trials": trials}

        analysis["lps_done"] = [
            float(trial["done:lines"]) / float(trial["done:duration"]) * 1000
            for trial in trials
            if trial["status"] == "DONE"
        ]

        analysis["lps_timeout"] = [
            float(trial["timeout:lines"]) / float(trial["timeout:time"]) * 1000
            for trial in trials
            if trial["status"] == "FAILED" and trial["failed:reason"] == "TIMEOUT"
        ]

        analysis["lps_stats_median"] = statistics.median(
            analysis["lps_done"] + analysis["lps_timeout"]
        )

        if len(trials) > 0:
            analysis["environment"] = trials[0]["environment"]

        analyzed_results[benchmark] = analysis

    return analyzed_results
