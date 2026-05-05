"""Validate STEP_PROBLEM_CATALOG.json against schema/catalog.schema.json.

The schema lives in ``schema/catalog.schema.json`` (Draft 2020-12) and pins
field types, enums, and required keys. Any drift between the catalog
generator (``step_corpus._build_catalog_json``) and the schema should fail
this test loudly so the schema is updated alongside the catalog.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

try:
    from jsonschema import Draft202012Validator
    HAS_JSONSCHEMA = True
except ImportError:  # pragma: no cover - skip path
    HAS_JSONSCHEMA = False

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schema" / "catalog.schema.json"
CATALOG_PATH = ROOT / "STEP_PROBLEM_CATALOG.json"


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
def test_schema_is_itself_valid() -> None:
    """The schema document must be a valid Draft 2020-12 schema."""
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
def test_catalog_validates_against_schema() -> None:
    """STEP_PROBLEM_CATALOG.json conforms to schema/catalog.schema.json."""
    schema = json.loads(SCHEMA_PATH.read_text())
    catalog = json.loads(CATALOG_PATH.read_text())
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(catalog))
    if errors:
        first_3 = errors[:3]
        msgs = "\n".join(f"  {e.json_path}: {e.message}" for e in first_3)
        pytest.fail(
            f"{len(errors)} schema violation(s); first 3:\n{msgs}"
        )
