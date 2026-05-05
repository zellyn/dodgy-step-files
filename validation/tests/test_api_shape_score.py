"""Tests for the OCCT-API-shape scorer.

Two roles:

1. Guard the scorer itself (regex correctness, scoped fields).
2. Track the audit pass: as the LGPL+searchability audit rephrases entries,
   the corpus-wide score should drop. The :func:`test_corpus_score_below_ceiling`
   ratchet is updated downward when the audit makes progress; it never
   ratchets upward.
"""
from __future__ import annotations

from step_corpus._api_shape_score import (
    _SCORED_FIELDS,
    rank_catalog,
    score_entry,
)

# Ratchet: corpus total token-hits must stay at or below this number.
# Lower the ceiling whenever the audit makes a clean pass; never raise it.
CORPUS_HITS_CEILING = 50


def test_score_entry_clean() -> None:
    entry = {
        "title": "Two adjacent edges leave a tiny gap on a planar face",
        "description": "Wire ends do not coincide within tolerance.",
        "expected_kernel_behavior": "Close gap or report.",
        "notes": "",
    }
    score, hits = score_entry(entry)
    assert score == 0
    assert hits == {}


def test_score_entry_class_leak() -> None:
    entry = {
        "title": "FixGap2d misses tiny gaps",
        "description": "ShapeFix_Wire::FixGap2d returns wrong status",
        "expected_kernel_behavior": "Close gap.",
        "notes": "Compare BRepCheck_Wire results.",
    }
    score, hits = score_entry(entry)
    assert score >= 4, f"expected 4+ hits, got {score}: {hits}"
    assert "title" in hits
    assert "description" in hits
    assert "notes" in hits


def test_score_entry_ignores_unscored_fields() -> None:
    """Sources / reproducer are explicitly NOT scored; they may contain
    OCCT references as evidence/STEP-spec vocabulary respectively.
    """
    entry = {
        "title": "Tiny gap between two edges",
        "description": "Wire ends do not coincide within tolerance.",
        "sources": "OCCT ShapeFix_Wire::FixGap2d, src/ShapeFix/ShapeFix_Wire.cxx:123",
        "reproducer": "ADVANCED_FACE with two ORIENTED_EDGEs, ShapeFix_Wire would be invoked",
    }
    score, _ = score_entry(entry)
    # Despite ShapeFix_Wire being in the prompt material, scored fields are clean.
    assert score == 0


def test_scored_fields_set() -> None:
    """Sanity: only the four allowed fields are scanned."""
    assert set(_SCORED_FIELDS) == {
        "title",
        "description",
        "expected_kernel_behavior",
        "notes",
    }


def test_corpus_score_below_ceiling() -> None:
    """The corpus-wide API-shape ratchet.

    When the audit pass rephrases entries, this number drops. Update
    CORPUS_HITS_CEILING downward to lock in the gain. Never raise it.
    """
    rows = rank_catalog()
    total_hits = sum(r["score"] for r in rows)
    assert total_hits <= CORPUS_HITS_CEILING, (
        f"corpus accumulated {total_hits} OCCT-API token hits, ceiling is {CORPUS_HITS_CEILING}.\n"
        f"Either run the LGPL+searchability audit, or (if intentional) raise the ceiling "
        f"with the rationale documented in the commit."
    )


def test_no_entry_above_high_water() -> None:
    """No single entry should score >= 6.

    Entries that hit this number are over-indexed on OCCT vocabulary in the
    fields a bug reporter would search; they are top-priority audit targets.
    """
    rows = rank_catalog()
    over = [r for r in rows if r["score"] >= 6]
    assert not over, (
        "entries with extreme OCCT-API leakage:\n"
        + "\n".join(f"  {r['id']:<8} score={r['score']} {r['title']}" for r in over)
    )
