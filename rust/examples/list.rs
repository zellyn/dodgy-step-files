//! Print a summary of the embedded corpus.
//!
//! Run with: `cargo run --example list`

use dodgy_step_files::{by_tag, fixtures};
use std::collections::BTreeMap;

fn main() {
    let total = fixtures().count();
    println!("Embedded corpus: {total} fixtures\n");

    let mut by_sec: BTreeMap<&str, usize> = BTreeMap::new();
    for f in fixtures() {
        *by_sec.entry(f.entry.section.as_str()).or_default() += 1;
    }
    println!("By section:");
    for (sec, n) in &by_sec {
        println!("  {sec:8}  {n:4}");
    }

    println!("\nFirst 5 fixtures:");
    for f in fixtures().take(5) {
        println!(
            "  {} [{}] {:6} bytes — {}",
            f.entry.id,
            f.entry.section,
            f.step_bytes.len(),
            f.entry.title,
        );
    }

    println!("\nFirst 3 crash fixtures:");
    for f in by_tag("crash").take(3) {
        println!("  {}  {}", f.entry.id, f.entry.title);
    }
}
