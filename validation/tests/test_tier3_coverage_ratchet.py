"""Ratchet test: percentage of catalog entries with at least one tier-3
assertion must not drop below the documented threshold.

Tier-3 assertions encode geometric/runtime invariants that survive
Part-21 whitespace + comment normalization. The catalog grew from
~10% tier-3 coverage at the start of the B2 harvest (2026-06-18) to
**91.9%** after five batches (97 shape_null + 389 §12.2 + 517 §12.3+4
+ 430 §12.5–13 + 449 soft load==ok). This test enforces a soft floor
so future catalog additions either bring their own tier-3 assertion
or explicitly bump the floor downward.

Update protocol:
- If a deliberate addition of bare-byte entries drops coverage, bump
  COVERAGE_FLOOR downward in the SAME commit that introduces them.
- If a refactor lifts coverage, bump COVERAGE_FLOOR upward to lock
  in the gain.
- Never silently let coverage drift down.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
CATALOG_MD = ROOT / "STEP_PROBLEM_CATALOG.md"


# Coverage floor: percentage of entries that must have at least one
# `**Tier-3 assertion**:` line. Bumped 2026-06-18 from ~10% to 90%
# after the five-batch B2 harvest (current actual: 91.9%).
COVERAGE_FLOOR_PERCENT = 90.0


def _count_tier3_coverage() -> tuple[int, int]:
    """Return (entries_with_tier3, total_entries) from the markdown."""
    text = CATALOG_MD.read_text()
    entries = re.split(
        r"^### ([A-Za-z][a-z]*\d+(?:\.input)?)\s+—\s+",
        text,
        flags=re.MULTILINE,
    )[1:]
    total = 0
    with_t3 = 0
    for i in range(0, len(entries), 2):
        body = entries[i + 1] if i + 1 < len(entries) else ""
        next_match = re.search(r"\n### ", body)
        if next_match:
            body = body[: next_match.start()]
        total += 1
        if re.search(r"^- \*\*Tier-3 assertion\*\*:", body, re.M):
            with_t3 += 1
    return with_t3, total


def test_tier3_coverage_above_floor() -> None:
    with_t3, total = _count_tier3_coverage()
    assert total > 0, "catalog parse returned no entries"
    pct = 100.0 * with_t3 / total
    assert pct >= COVERAGE_FLOOR_PERCENT, (
        f"tier-3 coverage dropped to {pct:.1f}% "
        f"({with_t3}/{total}), below the {COVERAGE_FLOOR_PERCENT:.1f}% "
        f"floor. Either add tier-3 assertions to the new entries, or "
        f"bump COVERAGE_FLOOR_PERCENT downward in this test file with "
        f"a one-line rationale in the same commit."
    )


def test_coverage_floor_is_not_aspirational() -> None:
    """Sanity: the floor is below the current actual coverage so that
    the test passes today. If you change the floor, you must keep this
    invariant or bump both numbers in lockstep."""
    with_t3, total = _count_tier3_coverage()
    pct = 100.0 * with_t3 / total
    assert pct >= COVERAGE_FLOOR_PERCENT, (
        f"floor {COVERAGE_FLOOR_PERCENT} >= current coverage {pct:.1f}; "
        "this would always fail. Either lower the floor or fix the catalog."
    )
