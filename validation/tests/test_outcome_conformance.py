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


def test_violate_disallowed_rate_stable(conformance_rows) -> None:
    """The violate-disallowed RATE should stay stable, not the raw count.

    This was an absolute ceiling (100 -> 101 -> 105) until 2026-08-08, when it
    went red at 115 and stayed red. The cause was not a kernel update or an
    extractor regression -- it was the spec-coverage pass. An entry can only be
    counted here if its `Expected kernel behavior` prose yields a `disallowed`
    tag; entries with no prose produce no tags and are invisible. Writing specs
    for ~620 more entries grew the POOL the ratchet draws from by a third
    (measured from the catalog text alone, no oracle: 284 -> 383 entries
    carrying a disallowed tag). The count rose because the corpus documents
    more, which is the goal -- so an absolute ceiling penalised exactly the
    work it should have been blind to.

    A rate is scale-free and measures what the docstring always claimed to
    care about: whether the relationship between what the catalog forbids and
    what the kernel actually does has shifted. Growth in the pool moves
    numerator and denominator together; a kernel change or a broken extractor
    moves only one.

    Two assertions, because the rate alone can be gamed by an empty denominator:

    - POOL FLOOR. Entries with no oracle output classify as `no-oracle` and
      can never be counted as violations. If the corpus sweep produces nothing
      (empty /tmp/cad-v2-out), every row becomes `no-oracle` and the violation
      count is 0 — so the old absolute assert passed vacuously on no data.
      (`test_conform_count_floor` did still catch that case, so the module was
      never fully blind; this makes the guard local to the assertion that
      needs it, rather than relying on a sibling test.) Verified by running
      this module against an empty /tmp/cad-v2-out: the floor fires.
    - RATE CEILING. The actual signal.

    Denominator deliberately requires BOTH a disallowed tag AND oracle output,
    matching the numerator's preconditions exactly. Counting oracle-less
    entries (Me* mesh, Ip* import) in the denominator would dilute the rate and
    let a real spike hide behind corpus growth.

    Measured 2026-08-08 on run 31247311065 (9a4576d2, full sweep, 2697 ok):
    pool=401, violations=115, rate=28.7%. That rate is DOWN from ~35% before
    the spec pass, while the raw count rose 105 -> 115.
    """
    pool = [r for r in conformance_rows
            if r["disallowed"] and r["verdict"] != "no-oracle"]
    viol = [r for r in conformance_rows if r["verdict"] == "violate-disallowed"]

    assert len(pool) >= 300, (
        f"only {len(pool)} entries have both a disallowed tag and oracle "
        f"output (expected 400+). Either the corpus sweep did not populate "
        f"/tmp/cad-v2-out or the outcome extractor stopped emitting tags — "
        f"without a denominator the rate below is meaningless."
    )

    rate = len(viol) / len(pool)
    assert rate <= 0.35, (
        f"violate-disallowed rate {rate:.1%} ({len(viol)}/{len(pool)}) exceeds "
        f"35%; kernel update or extractor regression? Note this is a RATE — "
        f"adding specced entries alone should not move it."
    )


def test_no_no_oracle_entries(conformance_rows) -> None:
    """Every entry should have an oracle baseline (validate2 output).

    Excludes Me* mesh fixtures — their oracle is the mesh-tier oracle
    (validation/src/step_corpus/_mesh_oracle.py), not validate2 — and
    Ip* §12.15 import-format fixtures, which are raw non-STEP files
    graded against external loaders (assimp/trimesh), not any wired
    oracle in this repo.
    """
    no_oracle = [r for r in conformance_rows
                 if r["verdict"] == "no-oracle"
                 and not r["id"].startswith("Me")
                 and not r["id"].startswith("Ip")]
    if no_oracle:
        ids = ", ".join(r["id"] for r in no_oracle[:10])
        pytest.fail(f"{len(no_oracle)} entries lack oracle output: {ids}")
