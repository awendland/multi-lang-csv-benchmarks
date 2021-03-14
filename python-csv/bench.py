import csv
import datetime
import json
import os
import sys
import time


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


input_csv_str = os.environ.get("BENCH_IN_CSV", "-")
output_tsv_str = os.environ.get("BENCH_OUT_TSV", "-")

eprint(f"reading from '{input_csv_str}'")
eprint(f"writing to '{output_tsv_str}'")

input_csv = sys.stdin if input_csv_str == "-" else open(input_csv_str, "r")
output_tsv = sys.stdout if output_tsv_str == "-" else open(output_tsv_str, "w")

writer = csv.writer(
    output_tsv, delimiter="\t", quoting=csv.QUOTE_MINIMAL, lineterminator="\n"
)

start = time.perf_counter()

for line in csv.reader(input_csv):
    writer.writerow(line)

elapsed = round((time.perf_counter() - start) * 1000)
eprint(f"completed in {elapsed} ms")

with open("performance", "a") as performance_file:
    performance_file.write(
        json.dumps(
            {
                "recorded_at": datetime.datetime.now().isoformat(),
                "duration": elapsed,
                "env_args": {k: v for (k, v) in os.environ.items() if "BENCH_" in k},
            }
        )
        + "\n"
    )
