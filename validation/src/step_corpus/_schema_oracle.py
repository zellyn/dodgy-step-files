"""Schema-vocabulary validation oracle.

For a STEP fixture, check that the entity types appearing in DATA are
permitted by the declared FILE_SCHEMA. Flags AP203-or-AP214-declared
files that use AP242-only entity types, the most common §12.8
schema-mismatch defect class.

This is a *vocabulary* check, not a full EXPRESS schema validator.
A full validator (entity-attribute arities, type hierarchy, derived
attributes) would require all-of-EXPRESS infrastructure; the
vocabulary check catches the bulk of practically-occurring schema
mismatches with two orders of magnitude less code.

Schema sets are curated from public AP203 / AP214 / AP242 entity
listings. Anything not in a schema's set, but present in a fixture
declaring that schema, is flagged.

Usage::

    cd validation
    uv run python -m step_corpus._schema_oracle ../step-examples/12-8-mixed/M002.stp
    uv run python -m step_corpus._schema_oracle           # all fixtures, summary
    uv run python -m step_corpus._schema_oracle --json    # full JSON output
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from step_corpus import catalog
from step_corpus._build_catalog_json import RESEARCH_ROOT


# Entity types that are AP242-only (not in AP203 or AP214). Curated from
# public AP242 documentation; expand as catalog evidence requires.
# Names are stored uppercase for case-insensitive matching.
AP242_ONLY = frozenset({
    # Tessellated geometry (introduced in AP242)
    "TESSELLATED_SHAPE_REPRESENTATION",
    "TESSELLATED_SOLID",
    "TESSELLATED_SHELL_REPRESENTATION",
    "TESSELLATED_FACE",
    "TRIANGULATED_FACE",
    "COMPLEX_TRIANGULATED_FACE",
    "COMPLEX_TRIANGULATED_SURFACE_SET",
    "COORDINATES_LIST",
    "TESSELLATED_VERTEX",
    "TESSELLATED_EDGE",
    "TESSELLATED_WIRE",
    "TESSELLATED_CONNECTING_EDGE",
    "TESSELLATED_CURVE_SET",
    "TESSELLATED_POINT_SET",
    "TESSELLATED_GEOMETRIC_SET",
    "TRIANGULATED_SURFACE_SET",
    # Feature definition
    "COMPOSITE_FEATURE",
    "COMPOSITE_HOLE",
    "ROUND_HOLE",
    "COUNTERBORE_HOLE",
    "COUNTERSUNK_HOLE",
    "RECTANGULAR_PATTERN",
    "CIRCULAR_PATTERN",
    "FEATURE_DEFINITION",
    "HOLE_BOTTOM",
    "BLIND_HOLE_BOTTOM",
    "THROUGH_HOLE_BOTTOM",
    # PMI specifically introduced in AP242 (others like ANNOTATION_PLANE,
    # DESCRIPTIVE_REPRESENTATION_ITEM, GENERAL_PROPERTY, PRESENTATION_VIEW
    # are shared with AP214 PMI extensions / representation_schema, so excluded).
    "DIMENSIONAL_LOCATION_WITH_PATH",
    "PROJECTED_ZONE_DEFINITION",
    "RUNOUT_ZONE_DEFINITION",
    "RUNOUT_TOLERANCE",
    "RUNOUT_TOLERANCE_WITH_DATUM",
    "DIMENSION_PAIR",
    "PRESENTATION_VIEW_ASSIGNMENT",
    # Kinematics, modernized in AP242
    "KINEMATIC_JOINT",
    "KINEMATIC_LINK",
    "KINEMATIC_LINK_REPRESENTATION",
    "KINEMATIC_PROPERTY_OF_PRODUCT",
    "KINEMATIC_TOPOLOGY_REPRESENTATION",
    "ANTI_PARALLEL_COMPOSED_LINK",
    # Composite-table / FEM hybrid
    "COMPOSITE_PROPERTY",
    "LAMINATE_TABLE",
    "LAMINATE_OR_PLY_DEFINITION",
    "PLY_BOUNDARY_REPRESENTATION",
    "PLY_LAMINA_DEFINITION",
    "PLY_LAYUP_TABLE",
    # ECAD (AP242 absorbed AP210)
    "VIA_DEFINITION",
    "NETWORK_NODE",
})

# Entity types specific to AP238 (STEP-NC). Out of place in AP203/AP214/AP242.
AP238_ONLY = frozenset({
    "MACHINING_OPERATION",
    "MACHINING_PROCESS_EXECUTABLE",
    "MACHINING_TOOL_FEEDSPEED",
    "WORKPLAN",
    "SETUP",
    "WORKPIECE_SETUP",
    "TRAJECTORY",
    "TWO5D_MILLING_OPERATION",
    "FREEFORM_MILLING_OPERATION",
    "DRILLING_OPERATION",
})

# Entity types specific to AP209 (FEA structural analysis).
AP209_ONLY = frozenset({
    "VOLUME_3D_ELEMENT_DESCRIPTOR",
    "CURVE_3D_ELEMENT_DESCRIPTOR",
    "SURFACE_3D_ELEMENT_DESCRIPTOR",
    "FEA_MODEL",
    "FEA_MODEL_3D",
    "ELEMENT_REPRESENTATION",
    "NODE_REPRESENTATION",
    "NODE_GROUP",
    "NODE_WITH_FORCE",
    "SINGLE_POINT_CONSTRAINT",
    "MULTI_POINT_CONSTRAINT",
})

# Fixtures whose catalog claim IS the schema-mismatch defect.
# These fixtures are EXPECTED to have schema-vocabulary violations:
# the violation is exactly what the catalog entry asserts. Strict mode
# treats *missing* violations on these as a regression (catalog claim
# silently weakened).
EXEMPT_SCHEMA_MISMATCH = {
    "Xp006",  # "Schema-mismatch × forward-reference × unresolved entity"
    "U018",   # "Tessellated annotation coordinates with no global unit context"
    "U037",   # "RescaleGeometry does not rescale triangulations"
    "A030",   # "Edition-mixed Part 21 file (header schema vs instance schema)"
    "A031",   # "Schema migration: retired AP214/AP203 kinematics entities"
    "M068",   # "Pretessellated geometry skipped on STEP write"
    "M069",   # "TRIANGULATED_FACE emitted without pnval indices"
    "M070",   # "STL writer does not respect existing triangulation"
    # Phase F regens (2026-06-18) — fixtures that demonstrate AP242 / AP238 /
    # AP210 defects using their native vocabulary while declaring the
    # AUTOMOTIVE_DESIGN schema (the Python builder only emits AP214 by
    # default; AP242-schema support is on the builder-extension backlog).
    "Tsh065",  # tessellated shell (TESSELLATED_SHELL_REPRESENTATION etc.)
    "M087",    # AP210 NETWORK_NODE
}

# Schema-name patterns that map to schema-IDs we care about.
# Each one tells us which "schema_id" the file declares (case-insensitive).
SCHEMA_NAME_PATTERNS = [
    (re.compile(r"AUTOMOTIVE_DESIGN", re.IGNORECASE), "AP214"),
    (re.compile(r"CONFIG_CONTROL_DESIGN", re.IGNORECASE), "AP203"),
    (re.compile(r"AP203", re.IGNORECASE), "AP203"),
    (re.compile(r"AP214", re.IGNORECASE), "AP214"),
    (re.compile(r"AP242|MANAGED_MODEL_BASED_3D_ENGINEERING", re.IGNORECASE), "AP242"),
    (re.compile(r"AP238|MACHINING|STEP_NC", re.IGNORECASE), "AP238"),
    (re.compile(r"AP209|STRUCTURAL_ANALYSIS_DESIGN", re.IGNORECASE), "AP209"),
    (re.compile(r"AP210|ELECTRONIC_ASSEMBLY", re.IGNORECASE), "AP210"),
]


_RE_FILE_SCHEMA = re.compile(rb"FILE_SCHEMA\s*\(\s*\(\s*'([^']+)'")
_RE_INSTANCE_DEF = re.compile(
    rb"(?:^|;)\s*#\d+\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.MULTILINE
)


def _detect_schema(body: bytes) -> str | None:
    m = _RE_FILE_SCHEMA.search(body)
    if not m:
        return None
    schema_str = m.group(1).decode("ascii", errors="replace")
    for pat, code in SCHEMA_NAME_PATTERNS:
        if pat.search(schema_str):
            return code
    return None


def _entity_types(body: bytes) -> set[str]:
    out: set[str] = set()
    # Strip /* */ comments and string literals so we don't see false matches
    text = body
    # Replace comment blocks with spaces (preserve length, simpler than full lex)
    text = re.sub(rb"/\*.*?\*/", b" ", text, flags=re.DOTALL)
    # Collapse string literals to ''
    text = re.sub(rb"'(?:[^']|'')*'", b"''", text, flags=re.DOTALL)
    for m in _RE_INSTANCE_DEF.finditer(text):
        out.add(m.group(1).upper().decode("ascii", errors="replace"))
    return out


def check_fixture(path: Path) -> dict[str, Any]:
    body = path.read_bytes()
    schema = _detect_schema(body)
    types = _entity_types(body)

    # Decide what's flagged for this schema
    forbidden_now: set[str] = set()
    if schema in {"AP203", "AP214"}:
        # AP242-only entities are not permitted
        forbidden_now |= AP242_ONLY
        # AP238/AP209 entities also not permitted
        forbidden_now |= AP238_ONLY
        forbidden_now |= AP209_ONLY
    elif schema == "AP242":
        # AP238/AP209 are separate APs; they shouldn't appear in AP242
        forbidden_now |= AP238_ONLY
        forbidden_now |= AP209_ONLY
    # AP238/AP209 entries declare their own schema; nothing forbidden.
    # If we couldn't detect a schema, skip; too risky to flag without context.

    violations = sorted(types & forbidden_now)
    return {
        "file": str(path),
        "schema": schema,
        "n_entity_types": len(types),
        "violations": violations,
    }


def check_all() -> list[dict[str, Any]]:
    rows = []
    for entry in catalog.iter_canonical():
        path = RESEARCH_ROOT / entry["fixture_path"]
        if not path.is_file():
            continue
        r = check_fixture(path)
        r["id"] = entry["id"]
        rows.append(r)
    return rows


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._schema_oracle")
    p.add_argument("paths", nargs="*", type=Path)
    p.add_argument("--all", action="store_true",
                   help="run on every catalog fixture")
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true",
                   help="exit 1 on unexpected violation OR missing exempt violation")
    args = p.parse_args(argv)

    if args.all or not args.paths:
        rows = check_all()
        if args.json:
            json.dump(rows, sys.stdout, indent=2)
            sys.stdout.write("\n")
            return 0
        from collections import Counter
        sch = Counter(r["schema"] for r in rows if r["schema"])
        no_schema = sum(1 for r in rows if r["schema"] is None)

        with_violations = [r for r in rows if r["violations"]]
        unexpected = [r for r in with_violations if r["id"] not in EXEMPT_SCHEMA_MISMATCH]
        expected_hits = {r["id"] for r in with_violations if r["id"] in EXEMPT_SCHEMA_MISMATCH}
        seen_ids = {r["id"] for r in rows}
        missing_exempt = sorted(eid for eid in EXEMPT_SCHEMA_MISMATCH
                                if eid in seen_ids and eid not in expected_hits)

        print(f"Schema-vocabulary check across {len(rows)} fixtures:")
        print(f"  schema undetected: {no_schema}")
        for s, n in sch.most_common():
            print(f"  {s}: {n}")
        print(f"\nExempt (catalog-claim-IS-mismatch) fixtures with expected violations: {len(expected_hits)}/{len(EXEMPT_SCHEMA_MISMATCH)}")
        if missing_exempt:
            print(f"  REGRESSION — exempt fixtures with no violation:")
            for eid in missing_exempt:
                print(f"    {eid}")
        print(f"\nUnexpected violations: {len(unexpected)}")
        for r in unexpected[:30]:
            v = ", ".join(r["violations"][:5])
            extras = "" if len(r["violations"]) <= 5 else f" (+{len(r['violations'])-5} more)"
            print(f"  {r['id']:<8}  {r['schema']:<6}  uses: {v}{extras}")
        if args.strict and (unexpected or missing_exempt):
            return 1
        return 0

    for path in args.paths:
        r = check_fixture(path)
        if args.json:
            json.dump(r, sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            print(f"{path.stem}: schema={r['schema']}  "
                  f"n_types={r['n_entity_types']}  "
                  f"violations={r['violations']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
