"""Schema-vocabulary oracle regression.

Locks two invariants:
  1. No fixture has an *unexpected* schema-vocabulary violation. New
     fixtures must declare a FILE_SCHEMA that matches their entity types.
  2. Every fixture in EXEMPT_SCHEMA_MISMATCH (catalog-claim-IS-mismatch)
     still exhibits its violation; if it stops violating, the catalog
     claim has been silently weakened by an edit elsewhere.
"""
from __future__ import annotations

import pytest

from step_corpus._schema_oracle import EXEMPT_SCHEMA_MISMATCH, check_all


@pytest.fixture(scope="module")
def oracle_rows() -> list[dict]:
    return check_all()


def test_no_unexpected_schema_violations(oracle_rows: list[dict]) -> None:
    unexpected = [
        r for r in oracle_rows
        if r["violations"] and r["id"] not in EXEMPT_SCHEMA_MISMATCH
    ]
    assert not unexpected, (
        "fixtures with unexpected schema-vocabulary violations:\n"
        + "\n".join(
            f"  {r['id']}  {r['schema']}  {r['violations']}"
            for r in unexpected
        )
    )


def test_exempt_fixtures_still_violate(oracle_rows: list[dict]) -> None:
    seen_ids = {r["id"] for r in oracle_rows}
    violators = {
        r["id"] for r in oracle_rows
        if r["violations"] and r["id"] in EXEMPT_SCHEMA_MISMATCH
    }
    missing = sorted(
        eid for eid in EXEMPT_SCHEMA_MISMATCH
        if eid in seen_ids and eid not in violators
    )
    assert not missing, (
        "EXEMPT_SCHEMA_MISMATCH fixtures whose catalog claim is no longer "
        f"witnessed by an oracle violation: {missing}. "
        "Either restore the schema/entity mismatch in the fixture, or "
        "remove the entry from EXEMPT_SCHEMA_MISMATCH."
    )
