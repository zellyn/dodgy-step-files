"""Sibling-pair fixture regression test.

Entries tagged ``provenance_tier: requires-sibling-pair`` describe
defects that manifest only by comparing a producer's *input* file to
its *output*. The catalog stores the post-defect state in
``<id>.stp`` and the pre-defect state in ``<id>.input.stp``.

This test confirms every requires-sibling-pair entry has both files
present; otherwise the catalog claim is unverifiable.
"""
from __future__ import annotations

import pytest

from step_corpus import catalog
from step_corpus._build_catalog_json import RESEARCH_ROOT


def test_sibling_pair_inputs_present() -> None:
    missing: list[str] = []
    for entry in catalog.iter_canonical():
        if entry.get("provenance_tier") != "requires-sibling-pair":
            continue
        # Look for sibling input alongside the main fixture
        main = RESEARCH_ROOT / entry["fixture_path"]
        sibling = main.with_name(main.stem + ".input.stp")
        if not sibling.is_file():
            missing.append(f"{entry['id']} → expected sibling at {sibling}")
    if missing:
        pytest.fail(
            f"{len(missing)} requires-sibling-pair entries lack their input fixture:\n"
            + "\n".join(f"  {m}" for m in missing)
        )
