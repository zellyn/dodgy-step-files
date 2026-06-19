"""Per-category lint regression.

The category-lint rules surface fixture-level issues (PMI fixtures with
no PMI entities, empty CLOSED_SHELL bodies, etc.) that the analysis
sub-agents identified.

Initial baseline (Apr 2026): 26 violations across the corpus.

This test is a *ratchet*: the count must not climb. As we fix more
fixtures, lower ``CATEGORY_LINT_CEILING`` to lock in the gain.
"""
from __future__ import annotations

from step_corpus import catalog
from step_corpus._category_lint import lint_one


# Ratchet: target is 0; currently 3 violations remain.
# Tsh077/Tsh136/Tsh183: intentional empty-shell bodies (the defect they
#   demonstrate — claim is "empty CLOSED_SHELL after writer pathology").
# Pmi106 ratched out 2026-06-19 — PMI regex now matches SHAPE_ASPECT +
# GEOMETRIC_ITEM_SPECIFIC_USAGE which the fixture emits.
CATEGORY_LINT_CEILING = 3


def test_category_lint_under_ceiling() -> None:
    rows: list[str] = []
    for entry in catalog.iter_canonical():
        for issue in lint_one(entry):
            rows.append(f"{entry['id']}: {issue}")
    n = len(rows)
    if n > CATEGORY_LINT_CEILING:
        listing = "\n".join(f"  {r}" for r in rows[:30])
        raise AssertionError(
            f"category-lint ceiling exceeded: {n} > {CATEGORY_LINT_CEILING}\n"
            f"first 30:\n{listing}"
        )
