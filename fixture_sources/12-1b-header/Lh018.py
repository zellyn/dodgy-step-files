"""Lh018 — Lower-case keyword (ifcperson, cartesian_point, ENTITY etc.).

Catalog claim: ISO 10303-21 keywords are upper-case. Hand-edited files routinely contain
lower-case or mixed-case (Cartesian_Point) entity names. Implementations that combine
case-insensitive lookup of internal keywords with case-sensitive comparison of
attribute-binding names produce two divergent parses for the same file.
Bug-reporter language: "lowercase keyword in STEP file", "ifcperson instead of IFCPERSON",
"cartesian_point in lowercase", "mixed-case entity name", "STEP entity not all caps".

Reproducer recipe: #1=ifcperson($,$,'',$,$,$,$,$);
  or #1=Cartesian_Point('',(0.,0.,0.));

Byte assertions:
  contains(b'cartesian_point') or contains(b'Cartesian_Point') or contains(b'ifcperson')
  matches(rb'EndSec;|End-Iso-10303-21;|cartesian_point|Cartesian_Point|ifcperson')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh018",
    defect=(
        "Lower-case keyword in DATA section (entity name not all upper-case); "
        "input: DATA section contains #1=Cartesian_Point('',(0.,0.,0.)) with mixed-case "
        "entity name instead of the required CARTESIAN_POINT; "
        "ISO 10303-21 keywords (entity names, attribute names, reserved words) must be upper-case; "
        "hand-edited files and some translators produce lower-case or mixed-case entity names "
        "such as Cartesian_Point, cartesian_point, or ifcperson; "
        "implementations combining case-insensitive lookup of internal keywords with "
        "case-sensitive attribute-binding comparison produce two divergent parses for the same file; "
        "per ISO, entity names canonicalize to upper-case before binding; "
        "expected kernel behavior: pick one rule (case-insensitive throughout) and apply uniformly; "
        "lenient mode may auto-uppercase with a warning; "
        "see also: Lh030; "
        "synonyms: lowercase keyword in STEP file, ifcperson instead of IFCPERSON, "
        "cartesian_point in lowercase, mixed-case entity name, STEP entity not all caps"
    ),
)


def _render_lh018() -> str:
    """Render a Part-21 with a lower-case/mixed-case entity name (Cartesian_Point)."""
    return (
        "ISO-10303-21;\n"
        "/* Lh018: lower-case / mixed-case entity name in DATA section */\n"
        "/* ISO 10303-21: all keywords and entity names must be upper-case */\n"
        "/* DEFECT: Cartesian_Point is mixed-case; spec requires CARTESIAN_POINT */\n"
        "/* Divergent parse: case-insensitive keyword lookup vs case-sensitive attribute binding */\n"
        "/* Produced by: hand-edited files, some CAD translators */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh018: lower-case entity name Cartesian_Point in DATA section'),'2;1');\n"
        "FILE_NAME('Lh018.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* DEFECT: Cartesian_Point uses mixed case instead of required CARTESIAN_POINT */\n"
        "#1=Cartesian_Point('',(0.,0.,0.));\n"
        "#2=Cartesian_Point('',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('lowercase-keyword-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh018(path) -> None:
    Path(path).write_text(_render_lh018())


f.render = _render_lh018  # type: ignore[method-assign]
f.write = _write_lh018    # type: ignore[method-assign]
