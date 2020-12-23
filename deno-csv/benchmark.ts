import { readCSV, CSVWriter } from "https://deno.land/x/csv@v0.5.1/mod.ts";

const inputCsvStr = Deno.env.get("BENCH_IN_CSV") ?? "-";
const outputTsvStr = Deno.env.get("BENCH_OUT_TSV") ?? "-";

console.warn(`reading from '${inputCsvStr}'`);
console.warn(`writing to '${outputTsvStr}'`);

let inputCsv = inputCsvStr == "-" ? Deno.stdin : await Deno.open(inputCsvStr);
let outputTsv =
  outputTsvStr == "-"
    ? Deno.stdout
    : await Deno.open(outputTsvStr, {
        write: true,
        truncate: true,
        create: true,
      });

const writer = new CSVWriter(outputTsv, { columnSeparator: "\t" });

let isFirstLine = true;
const start = performance.now();
for await (const row of readCSV(inputCsv)) {
  if (!isFirstLine) {
    await writer.nextLine();
  }
  isFirstLine = false;
  for await (const cell of row) {
    await writer.writeCell(cell);
  }
}
const elapsed = performance.now() - start;
console.warn(`completed in ${elapsed} ms`);

Deno.writeTextFileSync(
  "performance",
  JSON.stringify({
    recorded_at: new Date().toISOString(),
    duration: elapsed,
    env_args: Object.fromEntries(
      Object.entries(Deno.env.toObject()).filter(
        ([k, v]) => k.indexOf("BENCH_") == 0
      )
    ),
  })
);
