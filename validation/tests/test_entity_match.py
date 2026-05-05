"""Catalog↔fixture entity-citation drift test.

For every canonical catalog entry, confirm that the STEP entity-type tokens
named in its **Reproducer recipe** field show up in the matching fixture.
A low match ratio means catalog and fixture drifted out of sync.

Lenient on §12.10 (perf) and §12.11 (adversarial): those recipes describe
attack patterns rather than specific entity sets, so they are excluded from
the failure threshold (still reported via the entity-match report).

Run with: cd validation && uv run pytest tests/test_entity_match.py -v
"""

from __future__ import annotations

from pathlib import Path

from step_corpus.tier_entity_match import (
    check_fixture,
    extract_entry_blocks,
    extract_cited_entities,
    fixture_path_for_id,
    iter_canonical_entries,
    run_corpus,
)

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "STEP_PROBLEM_CATALOG.md"
EXAMPLES = ROOT / "step-examples"

# Entries whose match_ratio is below this count as failing.
THRESHOLD = 0.5
# Pytest fails the suite if more than this fraction of *concrete* entries
# (i.e. excluding §12.10 / §12.11) fall below THRESHOLD.
MAX_FAIL_FRACTION = 0.05


# ---------- unit checks on the four sample IDs the task pinned ----------


def test_le001_no_entities_perfect_match():
    """Le001 is byte-level (UTF-8 BOM); no entity tokens cited -> 1.0."""
    block = extract_entry_blocks(CATALOG.read_text())["Le001"]
    fpath = fixture_path_for_id(EXAMPLES, "Le001")
    r = check_fixture(fpath, block)
    assert r["cited"] == [], r
    assert r["match_ratio"] == 1.0


def test_tsh026_full_match():
    """Tsh026 cites ADVANCED_FACE / PLANE; both must be in the fixture."""
    block = extract_entry_blocks(CATALOG.read_text())["Tsh026"]
    fpath = fixture_path_for_id(EXAMPLES, "Tsh026")
    r = check_fixture(fpath, block)
    assert "ADVANCED_FACE" in r["cited"]
    assert "PLANE" in r["cited"]
    assert r["missing"] == [], r
    assert r["match_ratio"] == 1.0


def test_tfa011_partial_match_acceptable():
    """Tfa011 recipe lists ADVANCED_FACE / FACE_OUTER_BOUND / FACE_BOUND
    but the fixture intentionally only uses one of the two outer-bound
    variants. Match ratio is partial; still well above 0.5.
    """
    block = extract_entry_blocks(CATALOG.read_text())["Tfa011"]
    fpath = fixture_path_for_id(EXAMPLES, "Tfa011")
    r = check_fixture(fpath, block)
    assert "ADVANCED_FACE" in r["present"]
    assert "FACE_OUTER_BOUND" in r["present"]
    assert r["match_ratio"] >= 0.5, r


def test_pmi049_lowercase_recipe_perfect_match():
    """Pmi049's recipe uses lowercase tessellated_solid / styled_item, so
    no entity tokens are extracted; vacuously passes.
    """
    block = extract_entry_blocks(CATALOG.read_text())["Pmi049"]
    fpath = fixture_path_for_id(EXAMPLES, "Pmi049")
    r = check_fixture(fpath, block)
    assert r["cited"] == [], r
    assert r["match_ratio"] == 1.0


# ---------- denylist behaviour ----------


def test_extract_drops_keywords_and_short_tokens():
    text = "STEP file with `STRING` literal and `IFC` schema; cite `BOM`."
    assert extract_cited_entities(text) == []


def test_extract_keeps_real_entity_types():
    text = (
        "Build a `MANIFOLD_SOLID_BREP` whose `OPEN_SHELL` references "
        "`ADVANCED_FACE` instances on a `TOROIDAL_SURFACE`."
    )
    cited = extract_cited_entities(text)
    assert "MANIFOLD_SOLID_BREP" in cited
    assert "OPEN_SHELL" in cited
    assert "ADVANCED_FACE" in cited
    assert "TOROIDAL_SURFACE" in cited


# ---------- corpus-wide drift threshold ----------


def test_corpus_entity_match_under_threshold():
    """Fewer than 5% of concrete (non §12.10/§12.11) canonical entries
    may have match_ratio < 0.5. Drift in the catalog or fixtures will
    bump this count.
    """
    results = run_corpus(CATALOG, EXAMPLES)
    concrete = [r for r in results if not r["abstract"]]
    failing = [r for r in concrete if r["match_ratio"] < THRESHOLD]
    fraction = len(failing) / max(len(concrete), 1)
    msg = (
        f"{len(failing)} / {len(concrete)} concrete entries below "
        f"{THRESHOLD:.0%} match ({fraction:.2%}); threshold is "
        f"{MAX_FAIL_FRACTION:.0%}. Worst:\n"
        + "\n".join(
            f"  {r['id']:>6}  ratio={r['match_ratio']:.2f}  missing={r['missing']}"
            for r in sorted(failing, key=lambda x: x["match_ratio"])[:15]
        )
    )
    assert fraction < MAX_FAIL_FRACTION, msg


def test_corpus_runs_on_every_canonical_entry():
    """Every canonical entry with a recipe should resolve to a fixture
    file under step-examples/. Catches new IDs whose prefix isn't in
    the section map.
    """
    catalog_text = CATALOG.read_text()
    unmapped = []
    for eid, _block in iter_canonical_entries(catalog_text):
        fp = fixture_path_for_id(EXAMPLES, eid)
        if fp is None:
            unmapped.append(eid)
    assert not unmapped, f"unmapped IDs (add to _PREFIX_TO_DIR): {unmapped[:10]}"
