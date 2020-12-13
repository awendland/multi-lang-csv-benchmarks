use std::env;
use std::error::Error;
use std::fs::{File, OpenOptions};
use std::io;
use std::io::Write;
use std::process;
use std::time::{Duration, Instant};
extern crate chrono;
use chrono::Utc;

fn benchmark<R: io::Read, W: io::Write>(in_csv: R, out_tsv: W) -> Result<Duration, Box<dyn Error>> {
    let mut wtr = csv::WriterBuilder::new()
        .delimiter(b'\t')
        .from_writer(out_tsv);
    let mut rdr = csv::ReaderBuilder::new()
        .has_headers(false)
        .from_reader(in_csv);
    let now = Instant::now();
    for result in rdr.records() {
        let record = result?;
        wtr.write_record(&record)?;
    }
    wtr.flush()?;
    let dur = now.elapsed();
    eprintln!("completed in {} ms", dur.as_millis());
    Ok(now.elapsed())
}

fn main() {
    let in_csv_path = env::var("BENCH_IN_CSV").unwrap_or("-".to_string());
    eprintln!("reading from '{}'", in_csv_path);
    let in_csv: Box<dyn io::Read> = match in_csv_path.as_str() {
        "-" => Box::new(io::stdin()),
        path => Box::new(
            File::open(path).expect(format!("unable to open input file '{}'", path).as_str()),
        ),
    };
    let out_tsv_path = env::var("BENCH_OUT_TSV").unwrap_or("-".to_string());
    eprintln!("writing to '{}'", out_tsv_path);
    let out_tsv: Box<dyn io::Write> = match out_tsv_path.as_str() {
        "-" => Box::new(io::stdout()),
        path => Box::new(
            File::create(path).expect(format!("unable to open output file '{}'", path).as_str()),
        ),
    };

    match benchmark(in_csv, out_tsv) {
        Err(err) => {
            println!("error running benchmark: {}", err);
            process::exit(1);
        }
        Ok(runtime) => {
            let mut file = OpenOptions::new()
                .create(true)
                .append(true)
                .open("performance")
                .expect("unable to open 'performance' file");
            if let Err(err) = writeln!(
                &mut file,
                r#"{{"recorded_at": "{at}", "duration": {dur}, "in_csv": "{csv}", "out_tsv": "{tsv}"}}"#,
                at = Utc::now().to_rfc3339(),
                dur = runtime.as_millis(),
                csv = in_csv_path,
                tsv = out_tsv_path
            ) {
                println!("error saving benchmark results: {}", err);
                process::exit(2);
            }
        }
    }
}
