"""Regression test for the outcome-tag extractor.

The extractor maps catalog `**Expected kernel behavior**:` prose to
structured outcome tags (`heal`, `reject`, `warn-and-proceed`,
`silent-accept`, `crash`, `infinite-loop`). Pin a few canonical entries'
extractor output so future changes to either the prose or the regex set
get caught.
"""
from __future__ import annotations

import pytest

from step_corpus import catalog
from step_corpus._outcome_extractor import extract_outcomes, all_outcomes


@pytest.mark.parametrize(
    "entry_id, expect_allowed, expect_disallowed",
    [
        # Le001 (BOM): catalog says heal silently, reject UTF-16 BOMs
        ("Le001", {"heal", "reject"}, set()),
        # Lh002 (missing END marker): "fail-to-read" or similar
        ("Lh002", {"reject"}, set()),
        # Twi013 (small/sliver edges): healing-class
        ("Twi013", {"heal"}, set()),
        # A perf entry: no outcome tag expected, behavior described as scaling
        ("Pf001", set(), set()),
    ],
)
def test_extractor_pins(entry_id: str, expect_allowed: set, expect_disallowed: set) -> None:
    e = catalog.find(entry_id)
    if e is None:
        pytest.skip(f"entry {entry_id} not in catalog")
    out = extract_outcomes(e.get("expected_kernel_behavior") or "")
    if expect_allowed:
        assert expect_allowed.issubset(set(out["allowed"])), (
            f"{entry_id}: expected_allowed {expect_allowed} not subset of got {out['allowed']}\n"
            f"  prose: {e.get('expected_kernel_behavior')!r}"
        )
    if expect_disallowed:
        assert expect_disallowed.issubset(set(out["disallowed"])), (
            f"{entry_id}: expected_disallowed {expect_disallowed} not subset of got {out['disallowed']}"
        )


def test_extractor_covers_majority() -> None:
    """At least 50% of entries should get at least one outcome tag.

    Untagged entries are usually perf or process-state defects whose
    expected behavior is described in scaling terms; that's fine, but
    the bulk of normal heal/reject/warn entries should tag cleanly.
    """
    rows = all_outcomes()
    tagged = sum(1 for r in rows if r["allowed"] or r["disallowed"])
    pct = 100 * tagged / len(rows)
    assert pct >= 50, f"only {pct:.1f}% of entries got outcome tags ({tagged}/{len(rows)})"


def test_disallowed_dominates_when_explicit() -> None:
    """When prose says 'must not crash', the crash tag goes to
    disallowed, not allowed."""
    test_prose = "kernel must not crash; should heal silently"
    out = extract_outcomes(test_prose)
    assert "crash" in out["disallowed"]
    assert "heal" in out["allowed"]
