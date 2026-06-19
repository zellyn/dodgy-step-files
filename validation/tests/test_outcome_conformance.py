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
    """Total violate-disallowed should not exceed 105.

    Sudden spike means either kernel changed or the extractor's
    disallowed-tag logic broke; worth investigating. The ceiling was 100
    pre-v1.2.0; v1.2.0's nested-comment fix made 38 fixtures actually
    parse, so a handful now produce live oracle verdicts the
    pre-existing Expected lines didn't anticipate (count moved to 101).
    Bumping by +5 to leave headroom for the same shift on the in-flight
    v1.2.1 cube fixes; the ratchet should ratchet back DOWN as fidelity
    work continues.
    """
    n = sum(1 for r in conformance_rows if r["verdict"] == "violate-disallowed")
    assert n <= 105, (
        f"violate-disallowed count {n} exceeds 105; kernel update or "
        f"extractor regression?"
    )


def test_no_no_oracle_entries(conformance_rows) -> None:
    """Every entry should have an oracle baseline (validate2 output).

    Excludes Me* mesh fixtures — their oracle is the mesh-tier oracle
    (validation/src/step_corpus/_mesh_oracle.py), not validate2.
    """
    no_oracle = [r for r in conformance_rows
                 if r["verdict"] == "no-oracle"
                 and not r["id"].startswith("Me")]
    if no_oracle:
        ids = ", ".join(r["id"] for r in no_oracle[:10])
        pytest.fail(f"{len(no_oracle)} entries lack oracle output: {ids}")
