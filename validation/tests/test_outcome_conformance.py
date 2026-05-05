"""Track outcome conformance ratios over time.

The outcome-conformance check (`step_corpus._outcome_conformance`) reports
how many entries' live oracle behavior falls within the catalog's
declared `allowed` / `disallowed` outcomes. Mismatches are *informational*
(they document where OCC and the catalog disagree about what kernels
should do), but the *aggregate* should stay roughly stable. A sudden
collapse in the `conform` count would mean either:

- the outcome extractor regressed (broken regex)
- the live oracle changed (kernel update)
- the catalog text drifted in a way that broke the existing tag mapping

Any of those is worth a CI flag.
"""
from __future__ import annotations

import pytest

from step_corpus._outcome_conformance import report


@pytest.fixture(scope="module")
def conformance_rows():
    return report()


def test_conform_count_floor(conformance_rows) -> None:
    """At least 100 entries should land in `conform`."""
    n = sum(1 for r in conformance_rows if r["verdict"] == "conform")
    assert n >= 100, f"only {n} entries conform; outcome extractor or oracle may have regressed"


def test_violate_disallowed_below_ceiling(conformance_rows) -> None:
    """Total violate-disallowed should not exceed 100.

    Sudden spike means either kernel changed or the extractor's
    disallowed-tag logic broke; worth investigating.
    """
    n = sum(1 for r in conformance_rows if r["verdict"] == "violate-disallowed")
    assert n <= 100, (
        f"violate-disallowed count {n} exceeds 100; kernel update or "
        f"extractor regression?"
    )


def test_no_no_oracle_entries(conformance_rows) -> None:
    """Every entry should have an oracle baseline (validate2 output)."""
    no_oracle = [r for r in conformance_rows if r["verdict"] == "no-oracle"]
    if no_oracle:
        ids = ", ".join(r["id"] for r in no_oracle[:10])
        pytest.fail(f"{len(no_oracle)} entries lack oracle output: {ids}")
