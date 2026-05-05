"""Regression test for the bytes / tier-3 consistency audit.

Some catalog entries carry BOTH ``byte_assertions`` (raw-bytes claims)
and ``tier3_assertions`` (OCCT-parsed-geometry claims). These two kinds
of claim describe the same fixture and so must agree about that
fixture's identity. ``step_corpus._bytes_tier3_audit`` looks for pairs
that target the same dimension (face count, surface type, edge count)
and flags ones that contradict each other.

This test is a *ratchet*. The CEILING is the count of inconsistent
pairs at the time of authoring; new contradictions cannot be added
without either fixing them or explicitly bumping the ceiling.
"""
from __future__ import annotations

import pytest

from step_corpus._bytes_tier3_audit import audit_all

# Ratchet: number of `inconsistent` pair-records allowed today. Set to
# the value observed at the time this test was authored.
INCONSISTENT_CEILING = 0


@pytest.fixture(scope="module")
def audit_results() -> list[dict]:
    return audit_all()


def test_audit_runs_and_emits_records(audit_results: list[dict]) -> None:
    """At least one entry has both byte and tier-3 assertions today."""
    assert len(audit_results) >= 1, (
        "expected at least one pair-record; if the catalog has no entries "
        "with both kinds of assertion, this test no longer protects anything"
    )


def test_no_inconsistent_pairs(audit_results: list[dict]) -> None:
    """Ratchet: bytes/tier-3 contradictions must not exceed the ceiling."""
    inconsistent = [r for r in audit_results if r["verdict"] == "inconsistent"]
    if len(inconsistent) > INCONSISTENT_CEILING:
        listing = "\n".join(
            f"  {r['id']:<8} byte={r['byte_claim']!r} tier3={r['tier3_claim']!r}\n"
            f"           reason={r['reason']}"
            for r in inconsistent
        )
        pytest.fail(
            f"{len(inconsistent)} inconsistent bytes/tier-3 pairs (ceiling "
            f"is {INCONSISTENT_CEILING}):\n{listing}"
        )


def test_verdicts_are_well_formed(audit_results: list[dict]) -> None:
    allowed = {"consistent", "inconsistent", "uncheckable"}
    bad = [r for r in audit_results if r["verdict"] not in allowed]
    assert not bad, f"unexpected verdicts: {bad!r}"
