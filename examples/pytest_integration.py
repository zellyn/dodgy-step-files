"""Worked example: parameterize a CAD-kernel test suite over the corpus.

This is a template a downstream kernel author would copy into their own
project. It demonstrates:

- Iterating canonical catalog entries via the ``step_corpus`` package.
- Translating catalog entries into pytest parameterization.
- Asserting kernel behavior against the catalog's expected outcome.
- Marking known mismatches with ``pytest.xfail`` so your coverage
  matrix stays honest as the catalog grows.

Run with::

    cd validation && uv run pytest ../examples/pytest_integration.py -v

(In a real downstream project you'd install ``step_corpus`` as a
dependency from this repo's ``validation/`` package.)
"""
from __future__ import annotations

import pytest

from step_corpus import catalog


def your_kernel_load(fixture_path: str) -> dict:
    """Stub for your kernel's STEP loader.

    Replace with whatever entry-point your kernel exposes. The return shape
    is up to you; this template assumes a dict with at least these keys:

    - ``status``: "loaded" / "rejected" / "crashed"
    - ``shapes``: list of top-level shapes (may be empty)
    - ``warnings``: list of diagnostic strings
    """
    raise NotImplementedError("wire this to your kernel's API")


# Build the parameter list at import time. Each row is one catalog entry.
ENTRIES = list(catalog.iter_canonical())


def _entry_id(entry: dict) -> str:
    """Pytest test ID — concise, sortable, grep-friendly."""
    return entry["id"]


@pytest.mark.parametrize("entry", ENTRIES, ids=_entry_id)
def test_kernel_against_catalog(entry: dict) -> None:
    """One test per catalog entry — gate your kernel against each defect.

    This is the canonical shape: load the fixture, then assert the
    behavior the catalog says you should produce. Remove this skip once
    you've wired ``your_kernel_load``.
    """
    pytest.skip("template — wire your kernel's load function in your own project")

    # Real flow:
    #
    # result = your_kernel_load(entry["fixture_path"])
    #
    # # The catalog's `expected_kernel_behavior` field is prose ("heal",
    # # "reject with diagnostic E_X", "warn and continue", ...). Map your
    # # kernel's result to one of those positions and assert.
    # if "reject" in entry["expected_kernel_behavior"].lower():
    #     assert result["status"] == "rejected"
    # elif "heal" in entry["expected_kernel_behavior"].lower():
    #     assert result["status"] == "loaded"
    #     assert result["warnings"], "heal-and-warn was expected; no warnings emitted"
    # elif "warn" in entry["expected_kernel_behavior"].lower():
    #     assert result["status"] == "loaded"
    #     assert result["warnings"]


# Coverage-matrix helpers


def categorize_result(entry: dict, result: dict) -> str:
    """Classify a kernel result against catalog expectation.

    Returns one of: "pass", "xfail-known", "disagree-intentional",
    "unexpected".
    """
    expected = entry["expected_kernel_behavior"].lower()
    status = result.get("status", "")
    if "reject" in expected and status == "rejected":
        return "pass"
    if "heal" in expected and status == "loaded":
        return "pass"
    # ... extend with your own kernel's status taxonomy
    return "unexpected"
