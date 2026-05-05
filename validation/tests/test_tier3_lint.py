"""Tier-3 placeholder-geometry lint regression.

Locks the invariant that no NEW fixture introduces placeholder face
geometry (faces with edge_count==0 or degenerate areas) that masks the
catalog claim. The ratchet is set by ``_tier3_lint.CEILING``; ratchet
it down whenever a batch fix lands.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from step_corpus._tier3_lint import (
    CEILING,
    TIER3_CACHE,
    lint_from_cache,
)


@pytest.fixture(scope="module")
def cache_rows() -> list[dict]:
    if not TIER3_CACHE.is_file():
        pytest.skip(
            f"No tier-3 cache at {TIER3_CACHE}. "
            f"Run `uv run python -m step_corpus._tier3_lint --audit` to populate."
        )
    cache = json.loads(TIER3_CACHE.read_text())
    return lint_from_cache(cache)


def test_tier3_violations_under_ceiling(cache_rows: list[dict]) -> None:
    n = len(cache_rows)
    assert n <= CEILING, (
        f"Tier-3 placeholder-geometry violations: {n} (ceiling {CEILING}).\n"
        f"New fixtures introducing placeholder face geometry; either rewrite "
        f"with real bounded EDGE_LOOPs, or document the placeholder as "
        f"intentional and add to EXEMPT_PLACEHOLDER. Ceiling does not get "
        f"raised silently.\n"
        f"First 10 offenders:\n"
        + "\n".join(f"  {r['id']}: {r['issues'][0]}" for r in cache_rows[:10])
    )
