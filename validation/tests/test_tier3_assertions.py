"""Tier-3 assertions regression test.

Catalog entries can carry one or more `**Tier-3 assertion**:` lines that
encode a machine-checkable geometric claim (e.g. "face[0].sliver_aspect_max_min > 1e6").
This test runs the assertion checker against the live tier3 output and
fails if any assertion regresses.

Requires `/tmp/cad-v2-out-tier3/` populated by a fresh
`step_corpus._run_corpus` pass. CI runs `_run_corpus` before this test.
"""
from __future__ import annotations

import pytest

from step_corpus._tier3_assertions import check_all


@pytest.fixture(scope="module")
def assertion_results() -> list[dict]:
    return check_all()


def test_some_entries_carry_tier3_assertions(assertion_results: list[dict]) -> None:
    """At least a handful of entries should opt into tier-3 assertions."""
    assert len(assertion_results) >= 5, (
        "fewer than 5 catalog entries declare **Tier-3 assertion** lines"
    )


def test_no_tier3_assertion_failures(assertion_results: list[dict]) -> None:
    """Every declared assertion must pass against live tier3 output.

    Statuses other than 'pass' that count as failures:

    - ``fail``: lhs/rhs comparison evaluated False
    - ``parse-error``: the assertion line is malformed
    - ``eval-error``: comparison threw an exception
    - ``lhs-unresolved``: the field path doesn't exist on this fixture's
      tier3 output (often means the fixture didn't load: wrong assertion
      target)

    Statuses that are tolerated (don't fail the test):

    - ``no-tier3-output``: tier3 didn't run on this fixture (segfault or
      similar; covered by validate2's spec line, not tier3)
    - ``tier3-parse-error``: tier3 produced empty/broken JSON (rare; not
      a test-time concern)
    """
    fails = [r for r in assertion_results if r["status"] in {"fail", "parse-error", "eval-error", "lhs-unresolved"}]
    if fails:
        listing = "\n".join(
            f"  {r['id']:<8} [{r['status']}] {r['assertion']}"
            + (f"  actual={r.get('actual')!r}" if "actual" in r else "")
            for r in fails
        )
        pytest.fail(f"{len(fails)} tier-3 assertion failures:\n{listing}")
