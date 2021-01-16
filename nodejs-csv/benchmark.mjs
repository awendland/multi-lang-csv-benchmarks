import * as fs from "fs";
import { performance } from "perf_hooks";
import csv from "csv";

const inputCsvStr = process.env["BENCH_IN_CSV"] ?? "-";
const outputTsvStr = process.env["BENCH_OUT_TSV"] ?? "-";

console.warn(`reading from '${inputCsvStr}'`);
console.warn(`writing to '${outputTsvStr}'`);

let inputCsv =
  inputCsvStr == "-" ? process.stdin : fs.createReadStream(inputCsvStr);
let outputTsv =
  outputTsvStr == "-" ? process.stdout : fs.createWriteStream(outputTsvStr);

const start = performance.now();
const stream = inputCsv
  .pipe(csv.parse())
  .pipe(csv.stringify({ delimiter: "\t" }))
  .pipe(outputTsv)
  .on("error", (error) => console.error(error))
  .on("finish", () => {
    const elapsed = performance.now() - start;
    console.warn(`completed in ${elapsed} ms`);
    fs.appendFileSync(
      "performance",
      JSON.stringify({
        recorded_at: new Date().toISOString(),
        duration: elapsed,
        env_args: Object.fromEntries(
          Object.entries(process.env).filter(
            ([k, v]) => k.indexOf("BENCH_") == 0
          )
        ),
      }) + "\n"
    );
  });
