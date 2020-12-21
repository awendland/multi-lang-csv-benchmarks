# Multi-Language CSV Benchmarks

Comparison of CSV parsing and writing performance across multiple languages.

## Benchmark Structure

Each benchmark will self-report performance statistics. This is so extraneous runtime costs, such as initial file creation, runtime engine startup, module imports, and other such costs that will be amortized away in massive CSV processing operations do not skew the results. They will write (append) their performance results as newline-delimited JSON to `$BENCHMARK_DIR/performance`. The JSON will match the following schema:

```typescript
{
  "finished_at": string, // ISO 8601 date time
  "duration": number, // milliseconds
  "in_csv": string // path of input CSV file
}
```
