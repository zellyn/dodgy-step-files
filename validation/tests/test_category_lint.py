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


# Ratchet: target hit (0). All intentional empty-shell-IS-defect
# fixtures are now in EXEMPT_EMPTY_SHELL (Tsh023/077/136/183/Bo001);
# Pmi106 PMI regex extended; Pmi059/Pmi083 regained PMI chains.
CATEGORY_LINT_CEILING = 0


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
