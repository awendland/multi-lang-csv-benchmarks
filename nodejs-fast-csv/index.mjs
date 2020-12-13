import * as fs from 'fs';
import * as path from 'path';
import * as csv from 'fast-csv';

const outStream = fs.createWriteStream("test-direct-node.csv")

console.time()
let i = 0
const stream = fs.createReadStream(path.resolve('npidata_pfile_20050523-20201108.csv'))
    .pipe(csv.parse({ headers: false }))
    .on('error', error => console.error(error))
    .on('data', row => {
        process.stdout.write(".")
        outStream.write(row.join(", ") + "\n")
        if (++i > 3e4) {
            console.timeEnd()
            stream.destroy()
        }
    })
    .on('end', (rowCount) => console.log(`Parsed ${rowCount} rows`));