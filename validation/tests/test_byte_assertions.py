"""Byte-assertion regression test.

Catalog entries can carry one or more `**Byte assertion**:` lines that
encode a machine-checkable byte-level invariant. This test runs the
checker against the live fixture bytes and fails if any assertion no
longer holds.

Pair to ``test_tier3_assertions.py``: the same idea but for the
bytes-level subset (encoding / framing / syntax / adversarial / writer
pathology) where geometric tier-3 doesn't apply.
"""
from __future__ import annotations

import pytest

from step_corpus._byte_assertions import check_all


@pytest.fixture(scope="module")
def assertion_results() -> list[dict]:
    return check_all()


def test_some_entries_carry_byte_assertions(assertion_results: list[dict]) -> None:
    assert len(assertion_results) >= 200, (
        f"only {len(assertion_results)} byte-assertions registered; "
        f"expected >=200"
    )


def test_no_byte_assertion_failures(assertion_results: list[dict]) -> None:
    fails = [r for r in assertion_results if r["status"] != "pass"]
    if fails:
        listing = "\n".join(
            f"  {r['id']:<8} [{r['status']}] {r['assertion']}  detail={r['detail']}"
            for r in fails
        )
        pytest.fail(f"{len(fails)} byte-assertion failures:\n{listing}")
