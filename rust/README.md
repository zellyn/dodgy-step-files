# `dodgy-step-files` (Rust crate)

Embedded corpus of known-defective STEP / ISO 10303-21 files for testing CAD kernels.

Every fixture and the full catalog metadata is compiled into the crate via
[`include_dir`](https://crates.io/crates/include_dir) and `include_str!`, so
consumers don't have to clone the repo or set up any fixture directory.

The crate is not on crates.io — consume it as a git dependency, pinned to a
tag or commit:

```toml
[dependencies]
dodgy-step-files = { git = "https://github.com/zellyn/dodgy-step-files", tag = "v1.2.1" }
```

## Usage

```rust
use dodgy_step_files::{fixtures, fixture, by_tag, by_section};

// Iterate every fixture
for f in fixtures() {
    let _ = (f.entry.id.as_str(), f.entry.section.as_str(), f.step_bytes);
}

// Look up a single fixture by catalog id
let pf001 = fixture("Pf001").unwrap();
assert!(pf001.step_bytes.starts_with(b"ISO-10303-21"));

// Filter by defect class
for f in by_tag("crash") {
    // f.entry.taxonomy contains "crash"
}

// Filter by ISO 10303-21 section
for f in by_section("12.10") {
    // f.entry.section == "12.10"
}

// Open-shell fixtures: distinguish intended sheet bodies from
// accidentally-unclosed solids (heal targets). A solid-only kernel can
// cleanly refuse `Sheet` fixtures; it must heal `Solid` fixtures.
use dodgy_step_files::{by_closure_intent, ClosureIntent};
for f in by_closure_intent(ClosureIntent::Solid) {
    // f.entry.closure_defect: Option<ClosureDefect>
    // (Gap / MissingFace / UnstitchedSeam when known)
}
```

`Fixture` is `Copy`. It holds a `&'static CatalogEntry` and `&'static [u8]` —
both backed by the embedded data, so cloning is free.

## What's in `CatalogEntry`

Every entry has at least:

- `id`, `section`, `section_dir`, `fixture_path`
- `title`, `description`
- `taxonomy` (e.g. `["crash"]`, `["silent-loss", "topology"]`)
- `expected_validation` (raw string from the multi-tier oracle —
  e.g. `"occt=shape(1)/shape(1) gmsh=shape(32) ifc=schema_n/a"`)
- `severity` (`P0` / `P1` / `P2` / `P3` / `None`)
- `provenance_tier`, `category`, `sender`, `notes`
- `reproducer`, `expected_kernel_behavior`
- `byte_assertions`, `tier3_assertions` (raw Python-flavoured predicates the
  Python validator runs — from Rust they're documentation, not executable)
- `see_also`, `sources`
- `occ_behavior_note`, `cross_oracle_note`
- `closure_intent` (`Sheet` / `Solid` / `Ambiguous`, `None` when the fixture has no open-shell context) and `closure_defect` (`Gap` / `MissingFace` / `UnstitchedSeam`, set only when `closure_intent == Solid`)

See [`STEP_PROBLEM_CATALOG.md`](https://github.com/zellyn/dodgy-step-files/blob/main/STEP_PROBLEM_CATALOG.md)
for the human-readable version and
[`STEP_PROBLEM_CATALOG.json`](https://github.com/zellyn/dodgy-step-files/blob/main/STEP_PROBLEM_CATALOG.json)
for the machine-readable source.

## MSRV

Rust 1.80+ (uses `std::sync::LazyLock`).

## Binary size

The corpus is ~5.9 MB of `.stp` files plus a ~2.4 MB catalog JSON, so a test
binary linked against this crate gains roughly 8 MB. STEP is highly
compressible text and a future release may add a compressed-storage feature
flag; for now the design favors zero runtime decompression and zero
allocation on access.

## Example

```sh
cargo run --example list
```

Prints a per-section count and a few sample fixtures.

## License

MIT. See [LICENSE](https://github.com/zellyn/dodgy-step-files/blob/main/LICENSE).
