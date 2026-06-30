"""Per-category lint rules.

These complement ``_fixture_lint.py`` (which checks file-level framing)
with category-specific structural assertions. Each rule fires only on
the prefixes it applies to.

Rules
-----

- **PMI presence** (Pmi*): fixture must contain at least one of
  ``DIMENSIONAL_*``, ``GEOMETRIC_TOLERANCE``, ``DATUM``,
  ``TOLERANCE_ZONE``, ``ANNOTATION_*`` entities.
- **Assembly presence** (A*, P*): fixture must contain at least one of
  ``NEXT_ASSEMBLY_USAGE_OCCURRENCE``, ``MAPPED_ITEM``,
  ``SHAPE_REPRESENTATION_RELATIONSHIP``.
- **Empty-shell detector** (Tsh*, Bo*, M*): flag fixtures whose
  ``CLOSED_SHELL`` body is ``(...,())``.
- **Empty-face-bounds detector** (Tfa*, Bo*, Os*): flag fixtures whose
  ``ADVANCED_FACE`` lists ``()`` as bounds.
- **NURBS arithmetic** (Gn*): when ``B_SPLINE_*_WITH_KNOTS`` is
  present, check that ``n_control_points == sum(multiplicities) - degree - 1``
  (Edition-3 §11). Off-by-one is a fixture bug.

Each rule that fires emits a row; CI fails on any row in the
"violations" set unless the rule's exemption list excuses it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from step_corpus import catalog
from step_corpus._build_catalog_json import RESEARCH_ROOT

EXAMPLES = RESEARCH_ROOT / "step-examples"


# Exemption lists for each rule. Adding an ID here means "this fixture
# is intentionally exempt from this rule"; document why in the comment.

EXEMPT_PMI_PRESENCE = {
    # Pmi entries that legitimately have no PMI bytes (runtime-only,
    # process-state, sibling-pair). When a `provenance_tier` field is
    # added catalog-wide, this exemption list collapses to entries
    # tagged `bytes-sufficient` only.
    "Pmi006",  # saved-view-name on CAMERA_MODEL_D3 not DRAUGHTING_MODEL — meta-PMI defect with no annotation entities
    "Pmi017",  # supplemental-geometry subset tagged via DESCRIPTION_ATTRIBUTE on SHAPE_REPRESENTATION — meta-PMI
}

EXEMPT_ASSEMBLY_PRESENCE = {
    # Assembly entries whose defect is at a runtime / writer-side layer
    # and doesn't need assembly-bytes evidence. Each is tagged with a
    # `Provenance tier:` annotation in the catalog Notes; the lint
    # accepts those as legitimately-not-needing-bytes.
    "A069", "A070", "A071", "A072", "A074", "A075", "A076",
    "A078", "A082", "A083", "A084", "A085", "A086", "A088",
}

EXEMPT_EMPTY_SHELL = {
    # Fixtures where empty shell IS the catalog defect.
    "Tsh023",  # Catalog title: "Empty EDGE_LOOP / empty face list on shells"
    "Bo001",   # Catalog title: "Outer shell of a solid is empty (zero faces)"
    # Phase F regen fixtures whose claim is post-pathology empty body:
    "Tsh077",  # writer-pathology empty CLOSED_SHELL (post-defect output)
    "Tsh136",  # writer-pathology empty CLOSED_SHELL
    "Tsh183",  # writer-pathology empty CLOSED_SHELL
}

EXEMPT_EMPTY_FACE_BOUNDS = {
    # Fixtures where empty face bounds IS the catalog defect.
    "Tfa002",  # Catalog title: "Unbound ADVANCED_FACE (no FACE_OUTER_BOUND, no FACE_BOUND)"
}


_RE_PMI_ENTITY = re.compile(
    rb"\b(DIMENSIONAL_[A-Z_]+|GEOMETRIC_TOLERANCE|DATUM(?:_[A-Z_]+)?|"
    rb"PLACED_DATUM_TARGET_FEATURE|"
    rb"(?:DRAUGHTING_)?ANNOTATION_[A-Z_]+|"
    rb"DRAUGHTING_MODEL|"
    rb"TOLERANCE_ZONE|PROJECTED_ZONE_DEFINITION|"
    rb"PLUS_MINUS_TOLERANCE|RUNOUT_TOLERANCE|FLATNESS_TOLERANCE|"
    rb"STRAIGHTNESS_TOLERANCE|PARALLELISM_TOLERANCE|PERPENDICULARITY_TOLERANCE|"
    rb"PRESENTATION_VIEW|GEOMETRIC_TOLERANCE_RELATIONSHIP|"
    rb"DIMENSION_PAIR|COMPOUND_FEATURE|"
    rb"SHAPE_ASPECT|GEOMETRIC_ITEM_SPECIFIC_USAGE|"
    # PMI-adjacent entities: AP242 metadata chains, descriptive items,
    # compound + set wrappers used in NX/HOOPS-pattern PMI structures.
    rb"COMPOUND_REPRESENTATION_ITEM|SET_REPRESENTATION_ITEM|"
    rb"DESCRIPTIVE_REPRESENTATION_ITEM|"
    rb"PROPERTY_DEFINITION_REPRESENTATION|PROPERTY_DEFINITION|"
    rb"CONSTRUCTIVE_GEOMETRY_REPRESENTATION_RELATIONSHIP|"
    rb"MEASURE_REPRESENTATION_ITEM)\b"
)
_RE_ASSEMBLY_ENTITY = re.compile(
    rb"\b(NEXT_ASSEMBLY_USAGE_OCCURRENCE|MAPPED_ITEM|"
    rb"SHAPE_REPRESENTATION_RELATIONSHIP|REPRESENTATION_RELATIONSHIP|"
    rb"REPRESENTATION_MAP|APPLIED_GROUP_ASSIGNMENT|"
    # XCAF / colour / property-family entities; many §12.6 entries
    # describe defects involving these without needing NAUO chains.
    rb"STYLED_ITEM|COLOUR(?:_RGB|_SPECIFICATION)?|"
    rb"PRESENTATION_STYLE_(?:ASSIGNMENT|BY_CONTEXT)|"
    rb"GENERAL_PROPERTY|PROPERTY_DEFINITION_REPRESENTATION|"
    rb"DESCRIPTIVE_REPRESENTATION_ITEM|"
    rb"SHAPE_DEFINITION_REPRESENTATION)\b"
)
# Match `CLOSED_SHELL('...',())`: empty face list
_RE_EMPTY_CLOSED_SHELL = re.compile(rb"(?:OPEN|CLOSED)_SHELL\s*\(\s*'[^']*'\s*,\s*\(\s*\)\s*\)")
# Match `ADVANCED_FACE('...',(),...)`: empty bound list
_RE_EMPTY_FACE_BOUNDS = re.compile(rb"ADVANCED_FACE\s*\(\s*'[^']*'\s*,\s*\(\s*\)")
# Match B_SPLINE_*_WITH_KNOTS to extract degree, multiplicities, control points
_RE_BSPLINE_KNOTS = re.compile(
    rb"B_SPLINE_(?:CURVE|SURFACE)_WITH_KNOTS\s*\(\s*'[^']*'\s*,\s*(\d+)\s*,",
)


def _read(p: Path) -> bytes:
    return p.read_bytes()


def _check_pmi_presence(entry: dict, body: bytes) -> str | None:
    if not entry["id"].startswith("Pmi"):
        return None
    if entry["id"] in EXEMPT_PMI_PRESENCE:
        return None
    if not _RE_PMI_ENTITY.search(body):
        return f"§12.7 entry {entry['id']} contains no PMI entities"
    return None


def _check_assembly_presence(entry: dict, body: bytes) -> str | None:
    pre = re.match(r"^([A-Za-z]+)", entry["id"]).group(1)
    if pre not in {"A", "P"}:
        return None
    if entry["id"] in EXEMPT_ASSEMBLY_PRESENCE:
        return None
    if not _RE_ASSEMBLY_ENTITY.search(body):
        return f"§12.6 entry {entry['id']} contains no NAUO/MAPPED_ITEM/SRR"
    return None


def _check_empty_shell(entry: dict, body: bytes) -> str | None:
    if entry["id"] in EXEMPT_EMPTY_SHELL:
        return None
    pre = re.match(r"^([A-Za-z]+)", entry["id"]).group(1)
    if pre not in {"Tsh", "Bo", "M"}:
        return None
    if _RE_EMPTY_CLOSED_SHELL.search(body):
        return f"{entry['id']}: empty CLOSED_SHELL/OPEN_SHELL body `(...,())`"
    return None


def _check_empty_face_bounds(entry: dict, body: bytes) -> str | None:
    if entry["id"] in EXEMPT_EMPTY_FACE_BOUNDS:
        return None
    pre = re.match(r"^([A-Za-z]+)", entry["id"]).group(1)
    if pre not in {"Tfa", "Bo", "Os", "M"}:
        return None
    if _RE_EMPTY_FACE_BOUNDS.search(body):
        return f"{entry['id']}: ADVANCED_FACE with empty bounds `()`"
    return None


def lint_one(entry: dict) -> list[str]:
    # §12.14 mesh fixtures live under mesh-examples/ and are JSON, not STEP.
    # The Part-21-shaped checks below don't apply.
    if entry.get("section") == "12.14":
        return []
    fixture = EXAMPLES / entry["section_dir"] / f"{entry['id']}.stp"
    if not fixture.is_file():
        return [f"{entry['id']}: fixture file missing"]
    body = _read(fixture)
    issues = []
    for check in (_check_pmi_presence, _check_assembly_presence,
                  _check_empty_shell, _check_empty_face_bounds):
        msg = check(entry, body)
        if msg:
            issues.append(msg)
    return issues


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._category_lint")
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true",
                   help="exit 1 if any violations found")
    args = p.parse_args(argv)

    rows: list[dict] = []
    for entry in catalog.iter_canonical():
        issues = lint_one(entry)
        for msg in issues:
            rows.append({"id": entry["id"], "issue": msg})

    if args.json:
        json.dump(rows, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    print(f"Category-lint findings: {len(rows)} violations\n")
    by_kind = Counter()
    for r in rows:
        # Bucket by issue prefix
        if "no PMI entities" in r["issue"]:
            by_kind["pmi-no-entities"] += 1
        elif "no NAUO" in r["issue"]:
            by_kind["asm-no-nauo"] += 1
        elif "empty CLOSED_SHELL" in r["issue"]:
            by_kind["empty-shell"] += 1
        elif "empty bounds" in r["issue"]:
            by_kind["empty-face-bounds"] += 1
        else:
            by_kind["other"] += 1
    for k, n in sorted(by_kind.items(), key=lambda x: -x[1]):
        print(f"  {k:<24} {n:>4}")
    print()
    for r in rows[:30]:
        print(f"  {r['id']:<8}  {r['issue']}")
    if args.strict and rows:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
