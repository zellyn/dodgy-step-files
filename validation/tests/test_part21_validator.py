"""Regression tests for the pure-Python ISO 10303-21 validator.

Pin the validator's behavior on a small set of fixtures with known
spec-conformance properties. If a future change to the validator
silently shifts behavior on these, this test fails.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from step_corpus._build_catalog_json import RESEARCH_ROOT
from step_corpus._part21_validator import validate_file

EXAMPLES = RESEARCH_ROOT / "step-examples"


@pytest.mark.parametrize(
    "fixture, expected_status, expected_first_code",
    [
        # Clean fixture: well-formed Part-21, no warnings.
        ("12-3a-shells/Tsh007.stp", "accept", None),
        # UTF-8 BOM at start: spec allows but emits a warning.
        ("12-1a-encoding/Le001.stp", "accept_with_warnings", None),
        # Missing END-ISO-10303-21; close marker.
        ("12-1b-header/Lh002.stp", "reject", "E_NO_CLOSE"),
        # CR-only / DOS line endings: pure-Python validator can't find magic line.
        # (Demonstrates OCCT auto-heals what the spec leaves ambiguous.)
        ("12-1a-encoding/Le028.stp", "reject", None),
    ],
)
def test_validator_pins(fixture: str, expected_status: str, expected_first_code: str | None) -> None:
    f = EXAMPLES / fixture
    if not f.is_file():
        pytest.skip(f"fixture not present: {fixture}")
    v = validate_file(f)
    assert v.status == expected_status, (
        f"{fixture}: expected status={expected_status}, got={v.status}; "
        f"first_error={v.errors[:1]!r} first_warning={v.warnings[:1]!r}"
    )
    if expected_first_code is not None:
        codes = [e["code"] for e in v.errors]
        assert expected_first_code in codes, (
            f"{fixture}: expected error {expected_first_code} in {codes}"
        )


def test_validator_handles_empty_input() -> None:
    """An empty body should reject with E_NO_MAGIC, not crash."""
    from step_corpus._part21_validator import validate
    v = validate(b"")
    assert v.status == "reject"
    assert any(e["code"] == "E_NO_MAGIC" for e in v.errors)


def test_validator_counts_entities() -> None:
    """Spot-check entity-count is reasonable on a normal fixture."""
    f = EXAMPLES / "12-3a-shells/Tsh007.stp"
    if not f.is_file():
        pytest.skip("fixture not present")
    v = validate_file(f)
    assert v.n_entities >= 50, f"too few entities: {v.n_entities}"
    assert v.n_unresolved_refs == 0
