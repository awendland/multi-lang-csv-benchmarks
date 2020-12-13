import { readCSV, CSVWriter } from "https://deno.land/x/csv/mod.ts"
import yargs from "https://deno.land/x/yargs/deno.ts"
import { BufWriter, readStringDelim } from "https://deno.land/std@0.75.0/io/mod.ts"
import { StringWriter } from "https://deno.land/std@0.75.0/io/mod.ts"

const args = yargs(Deno.args).option("mode", {
  choices: ["sgr", "python-test", "debug"],
  default: "sgr",
}).argv
console.log(args)

const headersFile = await Deno.open(
  "npidata_pfile_20050523-20201108_FileHeader.csv"
) // Just the headers of a 7.8 GB, ~300 column CSV

const headers = []
for await (const row of readCSV(headersFile)) {
  for await (const cell of row) {
    headers.push(cell)
  }
  break
}

const headerFallback = "text"

const headerTypes: Record<string, string> = {
  NPI: "bigint",
  "Provider Enumaration Date": "timestamp",
  "Last Update Date": "timestamp",
  "NPI Deactivation Date": "timestamp",
  "NPI Reactivation Date": "timestamp",
  "Certification Date": "timestamp",
}

const cmds = {
  sgr: {
    cmd: [
      "/Users/awendland/.local/bin/poetry",
      "run",
      "sgr",
      "--verbosity=DEBUG",
      "csv",
      "import",
      "-k",
      "NPI",
      ...headers.map((h) => ["-t", h, headerTypes[h] ?? headerFallback]).flat(),
      "awendland/nppes-data-dissemination",
      "npidata",
    ],
    cwd: "/Users/awendland/code/others/splitgraph"
  },
  "python-test": {
    cmd: [
      "python",
      "-c",
      `import csv; import sys; print([len(l) for l in csv.reader(sys.stdin.readlines())])`,
    ],
  },
  debug: { cmd: ["sh", "-c", "cat - > test.csv"] },
}

const cmd = cmds[args.mode as keyof typeof cmds]
const p = Deno.run({ ...cmd, stdin: "piped" })

const te = new TextEncoder()
const teNL = te.encode("\n")

const outFile = await Deno.open("test-direct.csv", {write: true, truncate: true, create: true})
const buf = new BufWriter(outFile)
const writer = new CSVWriter(buf)
let arrBuf: Uint8Array[] = []

let isFirstLine = true
// Just reading rows - 8.5 sec
// writeCell to buf(def) file - 25 sec
// writeCell to buf(def) pipe sh - 25 sec
// custom write to buf(def) pipe sh - 21 sec
// custom write to buf(def) file - 20 sec
// custom write to file - very very slow
// custom Uint8Array[] buf write to file - ~20 sec
// readStringDelim and Deno.writeAll - 4 sec
// Just reading rows + cells - 10 sec
// Readings rows + cells and writing nl for rows buf(def) file - 10 sec
// Readings rows + cells and writing nl for rows and cells buf(def) file - 14 sec
console.time()
let i = 0
// for await (const line of readStringDelim(await Deno.open("npidata_pfile_20050523-20201108.csv"), "\n")) {
//   Deno.stdout.write(te.encode("."))
//   if (i % 10 == 0) {
//     await Deno.writeAll(outFile, te.encode(line))
//   }
//   if (++i > 3e4) break
// }
let c = 0
for await (const row of readCSV(
  await Deno.open("npidata_pfile_20050523-20201108.csv")
)) {
  if (!isFirstLine) {
    // await writer.nextLine()
    await buf.write(teNL)
    // arrBuf.push(teNL)
  }
  isFirstLine = false
  let isFirstRow = true 
  for await (const cell of row) {
    // await writer.writeCell(cell, {forceQuotes: true})
    // await buf.write(te.encode(`${isFirstRow ? "" : ","}"${cell}"`))
    c++;
    await buf.write(teNL)
    // arrBuf.push(te.encode(cell))
    isFirstRow = false
  }
  Deno.stdout.write(te.encode("."))
  // if (i % 10 == 0) {
  //   await Deno.writeAll(outFile, Uint8Array.from(arrBuf as unknown as Uint8Array))
  //   arrBuf = []
  // }
  if (++i > 3e4) break
}
await buf.flush()
console.log(c)
console.timeEnd()
p.stdin.close()

const { code } = await p.status()
Deno.exit(code)
