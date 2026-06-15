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
    /// For fixtures whose STEP bytes use `OPEN_SHELL` or
    /// `SHELL_BASED_SURFACE_MODEL`: was the open topology the intended final
    /// geometry (sheet), the symptom of an accidentally-unclosed solid (heal
    /// target), or undeterminable? `None` when the fixture has no open-shell
    /// context. A solid-only kernel can refuse `Sheet` fixtures cleanly; it
    /// must heal `Solid` fixtures rather than refuse them.
    pub closure_intent: Option<ClosureIntent>,
    /// When `closure_intent == Some(Solid)`, the defect kind that left the
    /// shell open. `None` when not applicable or not determinable.
    pub closure_defect: Option<ClosureDefect>,
    /// How the consumer should route the expectation for this fixture.
    /// Without this, a `conformance-probe` (legal-edge-case test where a
    /// correct kernel ACCEPTS) is indistinguishable from a
    /// `malformed-file` (where a correct kernel REJECTS) — and a
    /// `receiver-behavior` (valid file, buggy reader) is indistinguishable
    /// from either. `None` when not yet classified.
    pub fixture_kind: Option<FixtureKind>,
    /// When the defect requires comparing this fixture to a sibling
    /// (producer/receiver pair), the id of the sibling fixture. `None`
    /// when the fixture stands alone.
    pub pair_with: Option<String>,
}

/// Authored intent for an open-shell fixture.
#[derive(Deserialize, Debug, Clone, Copy, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum ClosureIntent {
    /// The open shell is the intended final geometry (sheet body / surface
    /// model). A solid-only kernel should cleanly refuse.
    Sheet,
    /// The fixture was authored as a solid that should close; openness is the
    /// defect. A repair-oriented kernel should heal it shut.
    Solid,
    /// Even with authoring intent the closure question is undeterminable —
    /// typically because the open shell is an incidental scaffold for a
    /// surface- or face-level defect that isn't fundamentally about closure.
    Ambiguous,
}

/// Defect kind that left a should-be-solid fixture open.
#[derive(Deserialize, Debug, Clone, Copy, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum ClosureDefect {
    /// Boundary edges almost meet but do not.
    Gap,
    /// A face that should be present is absent.
    MissingFace,
    /// Faces present but not joined along shared edges.
    UnstitchedSeam,
}

/// How a consumer should route the expectation for a fixture.
#[derive(Deserialize, Debug, Clone, Copy, PartialEq, Eq)]
#[serde(rename_all = "kebab-case")]
pub enum FixtureKind {
    /// The bytes themselves embody the defect. A correct kernel rejects,
    /// heals, or flags. This is the default kind for catalog entries
    /// whose claim is "this byte sequence is bad."
    MalformedFile,
    /// The file is fully legal Part-21 and tests that a correct kernel
    /// handles a legal edge case (e.g. Unicode at U+10FFFF, IEEE-754
    /// subnormals, exactly-at-limit values, every printable ASCII).
    /// A correct kernel ACCEPTS.
    ConformanceProbe,
    /// The file is valid; the defect is in how a buggy consumer
    /// reads/interprets it (e.g. silent unit mis-reads, attribute drops
    /// on round-trip). Express the expectation as "a correct reader does X."
    ReceiverBehavior,
    /// The defect lives in the TRANSFORM between two files; the test
    /// requires the sibling identified by `pair_with`. Invisible to a
    /// single-file consumer.
    ProducerReceiverPair,
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

/// Iterate fixtures whose `closure_intent` matches `intent`. Useful for
/// splitting open-shell fixtures into the "intended sheet body" vs
/// "accidentally-unclosed solid" sub-corpora — a solid-only kernel can
/// refuse the first cleanly but must heal the second.
pub fn by_closure_intent(
    intent: ClosureIntent,
) -> impl Iterator<Item = Fixture<'static>> {
    fixtures().filter(move |f| f.entry.closure_intent == Some(intent))
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

    #[test]
    fn closure_intent_labels_only_open_shell_fixtures() {
        let labelled: Vec<_> = fixtures()
            .filter(|f| f.entry.closure_intent.is_some())
            .collect();
        assert!(
            labelled.len() >= 200,
            "expected several hundred labelled open-shell fixtures, got {}",
            labelled.len()
        );
        for f in &labelled {
            let bytes = f.step_bytes;
            let has_open = bytes
                .windows(b"OPEN_SHELL".len())
                .any(|w| w == b"OPEN_SHELL");
            let has_sbsm = bytes
                .windows(b"SHELL_BASED_SURFACE_MODEL".len())
                .any(|w| w == b"SHELL_BASED_SURFACE_MODEL");
            assert!(
                has_open || has_sbsm,
                "{} carries closure_intent but bytes have no OPEN_SHELL or SBSM",
                f.entry.id
            );
        }
    }

    #[test]
    fn closure_defect_only_set_when_intent_is_solid() {
        for f in fixtures() {
            if f.entry.closure_defect.is_some() {
                assert_eq!(
                    f.entry.closure_intent,
                    Some(ClosureIntent::Solid),
                    "{} has closure_defect but intent is not Solid",
                    f.entry.id
                );
            }
        }
    }

    #[test]
    fn fixture_kind_labels_are_present_where_expected() {
        // The 1a conformance probes called out by the consumer feedback.
        for id in ["Ls005", "Ls030", "Le040", "Le045", "Le046", "Le047", "Ps004"] {
            let f = fixture(id).unwrap_or_else(|| panic!("{id} not in catalog"));
            assert_eq!(
                f.entry.fixture_kind,
                Some(FixtureKind::ConformanceProbe),
                "{id} should be labelled conformance-probe"
            );
        }
        // Producer/receiver pairs (the consumer-feedback set).
        for id in ["Le036", "Le049", "Le050", "A074", "Pmi090", "Ps011", "Wr043"] {
            let f = fixture(id).unwrap_or_else(|| panic!("{id} not in catalog"));
            assert_eq!(
                f.entry.fixture_kind,
                Some(FixtureKind::ProducerReceiverPair),
                "{id} should be labelled producer-receiver-pair"
            );
            assert_eq!(
                f.entry.pair_with.as_deref(),
                Some(format!("{id}.input").as_str()),
                "{id} pair_with mismatch"
            );
        }
    }
}
