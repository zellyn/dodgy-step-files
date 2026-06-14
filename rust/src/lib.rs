//! Embedded corpus of known-defective STEP / ISO 10303-21 files.
//!
//! Every fixture and its catalog metadata is compiled into the crate, so
//! consumers can iterate the corpus without any filesystem setup:
//!
//! ```no_run
//! for f in dodgy_step_files::fixtures() {
//!     println!("{} ({} bytes) — {}", f.entry.id, f.step_bytes.len(), f.entry.title);
//! }
//! ```
//!
//! The catalog is parsed lazily on first access. Looking up a single
//! fixture by id (`dodgy_step_files::fixture("Pf001")`) still walks the
//! catalog linearly; that's fast enough for the 1282-entry corpus and
//! avoids paying for an index nobody needs.

use include_dir::{include_dir, Dir};
use serde::Deserialize;
use std::sync::LazyLock;

/// One catalog entry, deserialized verbatim from `STEP_PROBLEM_CATALOG.json`.
///
/// `expected_validation` is left as the raw string from the catalog
/// (e.g. `"occt=shape(1)/shape(1) gmsh=shape(32) ifc=schema_n/a"`).
/// `byte_assertions` and `tier3_assertions` are also raw strings — they
/// encode Python-flavoured predicates that the Python validator runs;
/// from Rust they're documentation, not executable assertions.
#[derive(Deserialize, Debug, Clone)]
pub struct CatalogEntry {
    pub id: String,
    pub section: String,
    pub section_dir: String,
    pub title: String,
    pub description: String,
    pub fixture_path: String,
    pub taxonomy: Vec<String>,
    pub expected_validation: String,
    pub severity: Option<String>,
    pub provenance_tier: String,
    pub category: String,
    pub sender: Option<String>,
    pub notes: Option<String>,
    pub reproducer: String,
    pub expected_kernel_behavior: String,
    pub byte_assertions: Vec<String>,
    pub tier3_assertions: Vec<String>,
    pub see_also: Vec<String>,
    pub sources: Vec<String>,
    pub occ_behavior_note: Option<String>,
    pub cross_oracle_note: Option<String>,
}

/// A catalog entry paired with the raw bytes of its STEP file.
#[derive(Debug, Clone, Copy)]
pub struct Fixture<'a> {
    pub entry: &'a CatalogEntry,
    pub step_bytes: &'a [u8],
}

static STEP_EXAMPLES: Dir<'static> = include_dir!("$CARGO_MANIFEST_DIR/../step-examples");
const CATALOG_JSON: &str = include_str!("../../STEP_PROBLEM_CATALOG.json");

static CATALOG: LazyLock<Vec<CatalogEntry>> = LazyLock::new(|| {
    serde_json::from_str(CATALOG_JSON)
        .expect("embedded STEP_PROBLEM_CATALOG.json failed to parse")
});

fn step_bytes_for(fixture_path: &str) -> &'static [u8] {
    let in_dir = fixture_path
        .strip_prefix("step-examples/")
        .unwrap_or(fixture_path);
    STEP_EXAMPLES
        .get_file(in_dir)
        .unwrap_or_else(|| {
            panic!("embedded corpus is missing fixture file: {fixture_path}")
        })
        .contents()
}

/// Iterate every catalog entry paired with its STEP bytes.
pub fn fixtures() -> impl Iterator<Item = Fixture<'static>> {
    CATALOG.iter().map(|e| Fixture {
        entry: e,
        step_bytes: step_bytes_for(&e.fixture_path),
    })
}

/// Look up a fixture by catalog id (e.g. `"Pf001"`).
pub fn fixture(id: &str) -> Option<Fixture<'static>> {
    CATALOG
        .iter()
        .find(|e| e.id == id)
        .map(|e| Fixture {
            entry: e,
            step_bytes: step_bytes_for(&e.fixture_path),
        })
}

/// Iterate fixtures whose `taxonomy` contains `tag`
/// (e.g. `"crash"`, `"silent-loss"`, `"topology"`).
pub fn by_tag(tag: &str) -> impl Iterator<Item = Fixture<'static>> + '_ {
    fixtures().filter(move |f| f.entry.taxonomy.iter().any(|t| t == tag))
}

/// Iterate fixtures from a single ISO 10303-21 section
/// (e.g. `"12.10"`, `"12.3a"`).
pub fn by_section(section: &str) -> impl Iterator<Item = Fixture<'static>> + '_ {
    fixtures().filter(move |f| f.entry.section == section)
}

/// All catalog entries (without STEP bytes attached). Cheaper if you only
/// need metadata — no per-entry lookup into the embedded directory.
pub fn catalog() -> &'static [CatalogEntry] {
    &CATALOG
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn catalog_parses_to_expected_count() {
        assert_eq!(catalog().len(), 1282);
    }

    #[test]
    fn every_entry_resolves_to_nonempty_step_bytes() {
        for f in fixtures() {
            assert!(
                !f.step_bytes.is_empty(),
                "fixture {} resolved to empty bytes",
                f.entry.id
            );
        }
    }

    #[test]
    fn lookup_by_id_returns_matching_fixture() {
        let f = fixture("Pf001").expect("Pf001 should be in the catalog");
        assert_eq!(f.entry.section, "12.10");
        // Fixtures may begin with a prelude comment; the ISO header lives
        // somewhere inside. Don't require it to be the first bytes.
        assert!(!f.step_bytes.is_empty());
    }

    #[test]
    fn most_fixtures_contain_iso_header() {
        // Pure-binary or header-mangled fixtures are intentional, but
        // the vast majority should still contain the ISO-10303-21 marker.
        let with_header = fixtures()
            .filter(|f| f.step_bytes.windows(12).any(|w| w == b"ISO-10303-21"))
            .count();
        let total = fixtures().count();
        assert!(
            with_header * 100 / total >= 80,
            "expected >=80% of fixtures to contain ISO-10303-21 header, got {with_header}/{total}"
        );
    }

    #[test]
    fn by_tag_returns_only_tagged_fixtures() {
        let crashes: Vec<_> = by_tag("crash").collect();
        assert!(
            crashes.len() >= 50,
            "expected many crash fixtures, got {}",
            crashes.len()
        );
        for f in crashes {
            assert!(f.entry.taxonomy.iter().any(|t| t == "crash"));
        }
    }

    #[test]
    fn by_section_returns_only_section_fixtures() {
        for f in by_section("12.10") {
            assert_eq!(f.entry.section, "12.10");
        }
    }
}
