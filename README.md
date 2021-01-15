# Multi-Language CSV Benchmarks

Comparison of CSV parsing and writing performance across multiple languages.

## Benchmark Structure

Each benchmark will self-report performance statistics. This is so extraneous runtime costs, such as initial file creation, runtime engine startup, module imports, and other such costs that will be amortized away in massive CSV processing operations do not skew the results.

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
  "run:csv_to_tsv": string[] // command to run a benchmark converting a CSV to a TSV; expects BENCH_IN_CSV and BENCH_IN_TSV to be present in env vars
}
```
