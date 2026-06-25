"""Catalog-integrity tests for STEP_PROBLEM_CATALOG.json.

These tests guard against regressions in the markdown -> JSON pipeline:

- the JSON loads as a list,
- every entry has the documented required keys,
- every fixture_path actually points at an on-disk ``.stp`` file,
- the entry count stays in the expected range,
- the JSON re-serialises byte-identically when round-tripped through
  ``_build_catalog_json``.

Run with::

    cd validation && uv run pytest tests/test_catalog.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

from step_corpus import catalog
from step_corpus._build_catalog_json import (
    CATALOG_JSON,
    CATALOG_MD,
    RESEARCH_ROOT,
    build_catalog,
    write_catalog,
)

REQUIRED_KEYS = {
    "id",
    "title",
    "section",
    "section_dir",
    "category",
    "sources",
    "sender",
    "description",
    "reproducer",
    "expected_kernel_behavior",
    "notes",
    "expected_validation",
    "fixture_path",
    "see_also",
    # Structured fields promoted from prose
    "provenance_tier",
    "tier3_assertions",
    "byte_assertions",
    "cross_oracle_note",
    "occ_behavior_note",
}


@pytest.fixture(scope="module")
def entries() -> list[dict]:
    return catalog.load_catalog()


def test_catalog_loads_as_list(entries: list[dict]) -> None:
    assert isinstance(entries, list)
    assert all(isinstance(e, dict) for e in entries)


def test_entry_count_in_expected_range(entries: list[dict]) -> None:
    # Loose bound. Anything outside this band likely means parsing broke
    # or someone added a whole new section.
    # Range widened 2026-06-18: v3 OCCT deep-pass + waves 53-73 synthesis
    # grew the catalog from 1,282 → 2,302 entries.
    # Range widened 2026-06-23: mesh waves 19A-19C (Me530-Me555) added 24 entries.
    # Range widened 2026-06-24: mesh waves 15-39 merged in bulk (~700 mesh fixtures, total 3,049).
    assert 1000 <= len(entries) <= 3500, f"unexpected entry count: {len(entries)}"


def test_every_entry_has_required_keys(entries: list[dict]) -> None:
    for entry in entries:
        missing = REQUIRED_KEYS - entry.keys()
        assert not missing, f"{entry.get('id', '?')} is missing keys: {missing}"


def test_id_and_title_nonempty(entries: list[dict]) -> None:
    for entry in entries:
        assert entry["id"], f"entry has empty id: {entry!r}"
        assert entry["title"], f"{entry['id']} has empty title"


def test_ids_are_unique(entries: list[dict]) -> None:
    ids = [e["id"] for e in entries]
    duplicates = {i for i in ids if ids.count(i) > 1}
    assert not duplicates, f"duplicate ids in catalog: {sorted(duplicates)}"


def test_fixture_paths_exist(entries: list[dict]) -> None:
    missing: list[str] = []
    for entry in entries:
        fixture = RESEARCH_ROOT / entry["fixture_path"]
        if not fixture.is_file():
            missing.append(f"{entry['id']} -> {entry['fixture_path']}")
    assert not missing, "fixture files missing:\n" + "\n".join(missing)


def test_section_and_section_dir_consistent(entries: list[dict]) -> None:
    for entry in entries:
        section = entry["section"]
        section_dir = entry["section_dir"]
        # section_dir always starts with the section number with hyphens.
        # e.g. section "12.1a" -> dir starts with "12-1a-"
        prefix = section.replace(".", "-")
        assert section_dir.startswith(prefix), (
            f"{entry['id']}: section {section!r} does not match dir {section_dir!r}"
        )


def test_find_helper(entries: list[dict]) -> None:
    sample = entries[0]["id"]
    found = catalog.find(sample)
    assert found is not None
    assert found["id"] == sample
    assert catalog.find("DEFINITELY_NOT_AN_ID_XXX") is None


def test_iter_canonical_matches_load(entries: list[dict]) -> None:
    iter_list = list(catalog.iter_canonical())
    assert iter_list == entries


def test_json_roundtrip_is_byte_stable(tmp_path: Path) -> None:
    """Re-running the generator must produce a byte-identical JSON file."""
    target = tmp_path / "STEP_PROBLEM_CATALOG.json"
    rebuilt = build_catalog(CATALOG_MD)
    write_catalog(rebuilt, target)
    assert target.read_bytes() == CATALOG_JSON.read_bytes()


def test_no_orphan_fixtures(entries: list[dict]) -> None:
    """Every .stp / .mesh.json under step-examples/ + mesh-examples/ must
    have a catalog entry. Catches the "fixture committed without catalog
    entry" class of bug (Me270-279, Me620-624, Me630-639, Me810-812,
    Me932, P004 were all orphans found 2026-06-25 — backfilled).

    Sibling-input fixtures (*.input.stp) are intentionally not catalogued
    and are excluded from the check.
    """
    catalog_ids = {e["id"] for e in entries}

    on_disk: set[str] = set()
    for stp in RESEARCH_ROOT.glob("step-examples/12-*/[!_]*.stp"):
        if ".input" in stp.stem:
            continue  # sibling fixture; intentional
        on_disk.add(stp.stem)
    for mj in RESEARCH_ROOT.glob("mesh-examples/12-14-mesh/Me*.mesh.json"):
        on_disk.add(mj.stem.replace(".mesh", ""))

    orphans = sorted(on_disk - catalog_ids)
    assert not orphans, (
        f"{len(orphans)} fixture(s) on disk have no catalog entry — "
        f"add a `### <id> — ...` section to STEP_PROBLEM_CATALOG.md "
        f"for each:\n  " + "\n  ".join(orphans[:20])
        + ("\n  ..." if len(orphans) > 20 else "")
    )
