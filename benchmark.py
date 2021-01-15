from pathlib import Path
import argparse
import subprocess
import json
import logging
import sys
import shutil

benchmark_manifests = list(Path(__file__).parent.glob("*/benchmark.json"))
benchmark_names = {p.parent.stem: p for p in benchmark_manifests}

parser = argparse.ArgumentParser(description="Execute CSV processing benchmarks")
parser.add_argument(
    "benchmarks",
    nargs="+",
    choices=["all"] + list(benchmark_names.keys()),
    help="which benchmarks to execute",
)
parser.add_argument(
    "--log-level",
    default=logging.INFO,
    type=lambda l: getattr(logging, l),
    help="logging level",
)
parser.add_argument(
    "--mode",
    default="csv_to_csv",
    choices=["csv_to_tsv"],
    help="which CSV process to benchmark",
)
parser.add_argument(
    "--input-csv",
    default=Path(__file__).parent / "data-50k-lines.csv",
    type=lambda p: Path(p).resolve(),
    help="the well-formed CSV file to use as benchmark input",
)
parser.add_argument(
    "--timeout",
    default=5 * 60,  # seconds
    type=int,
    help="the maximum time (in seconds) that a benchmark can run before its terminated",
)
args = parser.parse_args()

logging.basicConfig(
    format=f'{"" if sys.stderr.isatty() else "%(levelname)s - "}%(message)s',
    level=args.log_level,
)

logging.info(
    "Found %d lines in input CSV file '%s'",
    sum(1 for line in open(args.input_csv)),
    args.input_csv,
)

if "all" in args.benchmarks:
    args.benchmarks = list(benchmark_names.keys())

results = {}

for benchmark in args.benchmarks:
    benchmark_manifest = benchmark_names[benchmark]
    benchmark_dir = benchmark_manifest.parent
    benchmark_performance = benchmark_dir / "performance"
    logging.info("BENCHMARK: %s", benchmark)
    try:
        benchmark_suite = json.loads(benchmark_manifest.read_text("utf8"))
        benchmark_out_file = (benchmark_dir / "out.tsv").resolve()

        cmd_env_vars = {
            "BENCH_IN_CSV": args.input_csv.resolve(),
            "BENCH_OUT_TSV": benchmark_out_file,
        }
        if benchmark_out_file.exists():
            benchmark_out_file.unlink()

        cmd_check_env = benchmark_suite["check:environment"]
        logging.info('%s: checking environment with "%s"', benchmark, cmd_check_env)
        subprocess.run(
            [shutil.which(cmd_check_env[0])] + cmd_check_env[1:],
            cwd=benchmark_dir,
            env=cmd_env_vars,
            stderr=subprocess.STDOUT,
            stdout=None
            if logging.getLogger().getEffectiveLevel() <= logging.INFO
            else subprocess.DEVNULL,
        )

        logging.debug("%s: reviewing previous benchmark results", benchmark)
        prev_results = []
        if benchmark_performance.exists():
            prev_results = benchmark_performance.read_text("utf8").strip().split("\n")
        if len(prev_results) > 0:
            prev_result = json.loads(prev_results[-1])
            logging.debug(
                "%s: previous benchmark was run at %s",
                benchmark,
                prev_result["recorded_at"],
            )

        cmd_run_benchmark = benchmark_suite["run:csv_to_tsv"]
        logging.info(
            '%s: benchmarking convert CSV to TSV with "%s"',
            benchmark,
            cmd_run_benchmark,
        )
        try:
            benchmark_run = subprocess.run(
                [shutil.which(cmd_run_benchmark[0])] + cmd_run_benchmark[1:],
                cwd=benchmark_dir,
                env=cmd_env_vars,
                stderr=subprocess.STDOUT,
                stdout=None
                if logging.getLogger().getEffectiveLevel() <= logging.DEBUG
                else subprocess.DEVNULL,
                timeout=args.timeout,
            )
            benchmark_run.check_returncode()

            logging.debug("%s: loading latest benchmark results", benchmark)
            latest_results = benchmark_performance.read_text("utf8").strip().split("\n")
            if len(latest_results) == 0:
                logging.error(
                    "%s: no benchmark results found at %s",
                    benchmark,
                    benchmark_performance,
                )
                continue
            latest_result = json.loads(latest_results[-1])
            if (
                prev_result is not None
                and latest_result["recorded_at"] == prev_result["recorded_at"]
            ):
                logging.error(
                    '%s: benchmark appears to have failed (the latest timestamp in "%s" did not change)',
                    benchmark,
                    benchmark_performance,
                )
                continue
            logging.info("%s: runtime was %d ms", benchmark, latest_result["duration"])
            results[benchmark] = latest_result["duration"]
        except subprocess.TimeoutExpired as e:
            logging.warning(
                "%s: benchmark exceeded %d second timeout", benchmark, round(e.timeout)
            )
            lines_written = sum(1 for line in open(cmd_env_vars["BENCH_OUT_TSV"]))
            logging.warning(
                "%s: wrote %d lines prior to termination", benchmark, lines_written
            )
            results[benchmark] = "TIMEOUT[lines=%d,time=%d]" % (
                lines_written,
                round(e.timeout * 1000),
            )
    except Exception as e:
        logging.exception(e)
        results[benchmark] = "FAILED"

for benchmark, result in results.items():
    print("%s\t%s" % (benchmark, result))
