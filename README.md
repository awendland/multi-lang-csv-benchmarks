# Multi-Language CSV Benchmarks

Comparison of CSV parsing and writing performance across multiple languages.

## Latest Results

Relative performance of _median lines / sec_ is the key focus. See [csv_to_tsv](#csv_to_tsv) for details about the benchmark. A timeout of 10 seconds was used. The input file was [data-50k-lines.csv](#data-50k-lines.csv).

<!-- report-start -->

| Language & Library | Median Lines / Sec | # Trials (# Failures) |
| ------------------ | ------------------ | --------------------- |
| deno-csv           | 49                 | 10 (10)               |
| nodejs-csv         | 7,908              | 10 (0)                |
| nodejs-fast-csv    | 2,645              | 10 (10)               |
| python-csv         | 27,001             | 10 (0)                |
| rust-csv           | 64,063             | 10 (0)                |

<!-- report-end -->

## Benchmark Structure

Each benchmark will self-report performance statistics. This is so extraneous runtime costs, such as initial file creation, runtime engine startup, module imports, and other such costs that will be amortized away in massive CSV processing operations do not skew the results.

### Benchmark Modes

#### csv_to_tsv

This benchmark will:

1. Ingest CSV formatted data from the filesystem
2. Convert each row to a TSV format (using quotes only when necessary)
3. Write the TSV to the filesystem

All steps are included in the trial's duration.

It's expected that the input CSV may be larger than memory and therefore must be handled in a streaming fashion.

### Benchmark Results

Each benchmark will write (append) their performance results as newline-delimited JSON to `$(pwd)/performance`. The JSON will match the following schema:

```typescript
{
  "recorded_at": string, // ISO 8601 date time
  "duration": number, // milliseconds
  "env_args": {} // all environment variables beginning with BENCH_
}
```

### Benchmark Manifest

Each benchmark will provide a JSON manifest at `$BENCHMARK_DIR/benchmark.json`. This manifest will contain:

```typescript
{
  "check:environment": string[], // command for loosely checking if the host environment has been correctly setup to run the benchmark
  "build:any": string[], // command for compiling the benchmarks into an executable form; "any" indicates that the build step works on all platforms, otherwise specify "OS:ARCH" where OS={macos,windows,linux} and ARCH={any,x64,x32,arm64,arm32}
  "run:csv_to_tsv": string[] // command to run a benchmark converting a CSV to a TSV; expects BENCH_IN_CSV and BENCH_IN_TSV to be present in env vars
}
```

### Benchmark Data

#### data-50k-lines.csv

Taken from the `npidata_pfile_20050523-20201108.csv` file in the `NPPES_Data_Dissemination_November_2020` dataset, a publicly accessible dataset containing information about doctors in the USA.

Features:

- 1 header row, 49,999 data rows.
- All fields are quoted and many fields are empty.
- Approximately 8k cells contain commas in them.
- No cells contain tabs.
