"""Regression ratchet for the cross-fixture dedup audit.

The dedup audit (`step_corpus._dedup_audit`) sweeps every pair of canonical
entries for high BM25 cross-similarity and classifies each pair into one of
``merge`` / ``cross-reference`` / ``keep``. We never auto-merge (merging
canonical entries changes the catalog's surface and demands human review),
but we *do* gate against drift: the count of ``merge`` suggestions at the
spec's nominal threshold (0.85) must not grow over time.

If this test fails with `merge_count > MERGE_CEILING`, do NOT raise the
ceiling without first investigating: the new merge suggestion likely
identifies a near-duplicate someone added without checking
``**See also**:`` first.

The audit also classifies low-similarity pairs as ``keep``; those are not
gated; legitimate diversity in the catalog is desirable.

Run with::

    cd validation && uv run pytest tests/test_dedup_audit.py -v
"""
from __future__ import annotations

import json
from pathlib import Path

from step_corpus._dedup_audit import (
    DEFAULT_THRESHOLD,
    apply_cross_references,
    classify_pair,
    run_audit,
)

# Regression ratchet: the count of ``merge`` suggestions at the default
# threshold from the v2 audit. Raise this only after auditing the new
# pair(s) and confirming they are intentionally not merged.
MERGE_CEILING = 0


def test_audit_at_default_threshold_runs_clean():
    """Audit at threshold 0.85 must produce ``merge_count <= MERGE_CEILING``.

    The catalog has gone through a v1 dedup pass already; new merge
    suggestions at 0.85 mean a contributor missed an existing canonical
    entry covering their defect class.
    """
    report = run_audit(DEFAULT_THRESHOLD)
    counts = report["counts"]
    assert report["threshold"] == DEFAULT_THRESHOLD
    assert report["n_entries"] >= 1000  # sanity
    merge_count = counts.get("merge", 0)
    assert merge_count <= MERGE_CEILING, (
        f"dedup audit found {merge_count} merge suggestion(s) at threshold "
        f"{DEFAULT_THRESHOLD} (ceiling={MERGE_CEILING}). Investigate the new "
        f"pair(s) before bumping MERGE_CEILING:\n"
        + "\n".join(
            f"  {p['a']} <-> {p['b']}  bm25={p['bm25_normalized']:.3f}  "
            f"category={p['a_category']}"
            for p in report["pairs"]
            if p["verdict"] == "merge"
        )
    )


def test_classify_pair_merges_same_class_with_byte_overlap():
    """Classifier returns ``merge`` only when category, taxonomy, and byte
    fingerprint all line up.
    """
    a = {
        "category": "§12.8 mixed (sub-class: AP238 deep machining)",
        "taxonomy": ["spec-violation"],
        "byte_assertions": [
            "contains(b'BORING_TOOL_BODY')",
            "contains(b'diameter < 0')",
        ],
    }
    b = {
        "category": "§12.8 mixed (sub-class: AP238 deep machining)",
        "taxonomy": ["spec-violation"],
        "byte_assertions": [
            "contains(b'BORING_TOOL_BODY')",
            "contains(b'diameter < 0')",
        ],
    }
    assert classify_pair(a, b) == "merge"


def test_classify_pair_cross_reference_when_taxonomy_diverges():
    """Same category but different taxonomy tags → ``cross-reference``."""
    a = {
        "category": "§12.7 (sub-class: annotation-plane)",
        "taxonomy": ["pmi"],
        "byte_assertions": [],
    }
    b = {
        "category": "§12.7 (sub-class: annotation-plane)",
        "taxonomy": ["pmi", "spec-violation"],
        "byte_assertions": [],
    }
    assert classify_pair(a, b) == "cross-reference"


def test_classify_pair_keeps_distinct_categories():
    """Different categories → ``keep`` (different defect domains)."""
    a = {
        "category": "§12.4 (sub-class: PMI numeric)",
        "taxonomy": ["pmi"],
        "byte_assertions": ["contains(b'PLUS_MINUS_TOLERANCE')"],
    }
    b = {
        "category": "§12.7 (sub-class: precision_qualifier)",
        "taxonomy": ["pmi"],
        "byte_assertions": ["contains(b'PLUS_MINUS_TOLERANCE')"],
    }
    assert classify_pair(a, b) == "keep"


def test_apply_cross_references_idempotent_at_default_threshold(tmp_path: Path):
    """Applying cross-refs at the default threshold is a no-op against the
    current catalog markdown; every pair at 0.85+ is already linked.

    The test copies the live catalog into a tmp dir and verifies that the
    ``--apply-cross-references`` path leaves it byte-for-byte unchanged.
    A future regression where a 0.85+ pair shows up unlinked would flip
    this assertion and surface the new candidate.
    """
    src_md = Path(__file__).resolve().parents[2] / "STEP_PROBLEM_CATALOG.md"
    dst_md = tmp_path / "STEP_PROBLEM_CATALOG.md"
    dst_md.write_bytes(src_md.read_bytes())
    before = dst_md.read_bytes()

    report = run_audit(DEFAULT_THRESHOLD)
    apply_cross_references(report["pairs"], catalog_md_path=dst_md)

    after = dst_md.read_bytes()
    assert before == after, (
        "apply_cross_references mutated the catalog at threshold "
        f"{DEFAULT_THRESHOLD}; expected no edits because every pair at this "
        "threshold should already be linked via **See also**."
    )


def test_audit_writes_json_report_shape():
    """The audit produces a JSON-serialisable dict with the documented
    shape; downstream tooling depends on this contract.
    """
    report = run_audit(DEFAULT_THRESHOLD)
    # All top-level keys present
    assert {"threshold", "n_entries", "n_pairs", "counts", "pairs"} <= set(
        report
    )
    # Round-trip through JSON to confirm serialisability
    payload = json.dumps(report)
    parsed = json.loads(payload)
    assert parsed["n_entries"] == report["n_entries"]
    # Each pair carries the documented fields
    for p in report["pairs"]:
        assert {
            "a",
            "b",
            "bm25_normalized",
            "cosine",
            "verdict",
            "a_category",
            "b_category",
            "byte_overlap",
            "already_linked",
        } <= set(p)
        assert p["verdict"] in {"merge", "cross-reference", "keep"}
