"""Tests for the cross-cutting defect-class taxonomy.

The taxonomy adds an orthogonal browse axis to the catalog: each entry
is tagged with 1-3 of 15 vocabulary tags describing the *kind* of defect
(crash, silent-loss, spec-violation, etc.) rather than its location in
the §12.x sectioning.

Invariants this module enforces:

- Every catalog entry receives at least one tag.
- Every emitted tag is in the canonical 15-tag vocabulary.
- The vocabulary has exactly 15 tags (drop deliberately requires explicit
  test edit so accidental growth fails CI).
"""
from __future__ import annotations

from step_corpus import _taxonomy, catalog


def test_tag_vocabulary_size() -> None:
    """Vocabulary stays at exactly 15 tags. Bumping requires explicit edit."""
    assert len(_taxonomy.TAG_VOCABULARY) == 15
    # Vocabulary is also deduplicated.
    assert len(set(_taxonomy.TAG_VOCABULARY)) == 15
    # And each tag has a description.
    for tag in _taxonomy.TAG_VOCABULARY:
        assert tag in _taxonomy.TAG_DESCRIPTIONS, (
            f"missing description for tag {tag!r}"
        )


def test_no_unknown_tags() -> None:
    """Only the 15-vocabulary tags are emitted by `derive`."""
    entries = catalog.load_catalog()
    for entry in entries:
        tags = entry.get("taxonomy") or _taxonomy.derive(entry)
        for t in tags:
            assert t in _taxonomy.TAG_SET, (
                f"entry {entry['id']} has unknown tag {t!r}"
            )


def test_every_entry_has_at_least_one_tag() -> None:
    """All catalog entries get tagged; no zero-tag entries allowed."""
    entries = catalog.load_catalog()
    untagged: list[str] = []
    for entry in entries:
        tags = entry.get("taxonomy") or _taxonomy.derive(entry)
        if not tags:
            untagged.append(entry["id"])
    assert not untagged, f"untagged entries: {untagged[:20]} (total {len(untagged)})"


def test_tag_size_bounds() -> None:
    """Each entry has between 1 and 3 tags."""
    entries = catalog.load_catalog()
    for entry in entries:
        tags = entry.get("taxonomy") or _taxonomy.derive(entry)
        assert 1 <= len(tags) <= 3, (
            f"entry {entry['id']} has {len(tags)} tags: {tags}"
        )


def test_known_crashes_get_crash_tag() -> None:
    """Spot-check: the well-known kernel-crash fixtures all carry `crash`."""
    known_crash_ids = ["Gp001", "Gn003", "Gn004", "Twi044", "U008", "U009"]
    by_id = {e["id"]: e for e in catalog.load_catalog()}
    for cid in known_crash_ids:
        entry = by_id.get(cid)
        if entry is None:
            continue  # entry was removed from catalog
        tags = entry.get("taxonomy") or _taxonomy.derive(entry)
        assert "crash" in tags, f"entry {cid} expected crash tag; got {tags}"


def test_section_derived_tags() -> None:
    """Spot-check: each section_dir's entries carry the section-derived tag."""
    entries = catalog.load_catalog()
    for entry in entries:
        sd = entry["section_dir"]
        expected = _taxonomy.SECTION_TO_TAG.get(sd)
        if expected is None:
            continue
        tags = entry.get("taxonomy") or _taxonomy.derive(entry)
        assert expected in tags, (
            f"entry {entry['id']} (section {sd}) missing section tag "
            f"{expected!r}; got {tags}"
        )


def test_derive_is_deterministic() -> None:
    """Calling `derive` twice on the same entry yields the same list."""
    entries = catalog.load_catalog()
    # Sample 20 entries
    step = max(1, len(entries) // 20)
    for entry in entries[::step][:20]:
        a = _taxonomy.derive(entry)
        b = _taxonomy.derive(entry)
        assert a == b, f"non-deterministic for {entry['id']}: {a} vs {b}"
        # And ordered by vocabulary position.
        order = [_taxonomy.TAG_VOCABULARY.index(t) for t in a]
        assert order == sorted(order), (
            f"tags for {entry['id']} not in vocabulary order: {a}"
        )
