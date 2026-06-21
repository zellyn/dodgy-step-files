"""Lh009 — Blank, mis-cased, or unrecognized schema name.

Catalog claim: FILE_SCHEMA value is '', mixed-case ('AutomotiveDesign'), uses a non-canonical
long form (e.g. _MIM instead of _MIM_LF), names an internal vendor schema, or comma-separates
multiple schemas inside one string instead of using a LIST.
Bug-reporter language: "empty FILE_SCHEMA value", "mixed-case schema name",
"vendor schema in FILE_SCHEMA", "comma-separated schemas inside one string",
"unrecognised schema name".

Reproducer recipe: FILE_SCHEMA(('AUTOMOTIVE_DESIGN_MIM')); (instead of _MIM_LF)

Byte assertions:
  matches(rb"FILE_SCHEMA\\(\\(\\s*'AUTOMOTIVE_DESIGN_MIM(?!_LF)'")
  contains(b'AUTOMOTIVE_DESIGN_MIM')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh009",
    defect=(
        "Blank, mis-cased, or unrecognized schema name in FILE_SCHEMA; "
        "input: FILE_SCHEMA contains a non-canonical schema identifier "
        "AUTOMOTIVE_DESIGN_MIM instead of the correct AUTOMOTIVE_DESIGN_MIM_LF; "
        "the truncated form omits the mandatory _LF suffix that denotes the "
        "Long Form (LF) subset required by ISO 10303-214; "
        "ISO 10303-21 §8 requires the schema name to match exactly one of the registered "
        "AP identifiers; mis-cased, truncated, or invented names leave receivers without "
        "a valid schema binding; "
        "expected kernel behavior: case-fold to upper for compare; "
        "warn-and-fall-back-to-best-fit on unrecognized names; "
        "reject the comma-in-string variant; "
        "see also: Lh006; "
        "synonyms: empty FILE_SCHEMA value, mixed-case schema name, vendor schema in FILE_SCHEMA, "
        "comma-separated schemas inside one string, unrecognised schema name, "
        "AUTOMOTIVE_DESIGN_MIM instead of AUTOMOTIVE_DESIGN_MIM_LF"
    ),
)


def _render_lh009() -> str:
    """Render a Part-21 where FILE_SCHEMA uses a non-canonical truncated schema name."""
    return (
        "ISO-10303-21;\n"
        "/* Lh009: FILE_SCHEMA uses non-canonical truncated schema name */\n"
        "/* ISO 10303-21 §8: schema name must match a registered AP identifier exactly */\n"
        "/* DEFECT: 'AUTOMOTIVE_DESIGN_MIM' is missing the required '_LF' suffix */\n"
        "/* Correct form: FILE_SCHEMA(('AUTOMOTIVE_DESIGN_MIM_LF')); */\n"
        "/* Receivers that do exact-match comparison will fail to bind the schema */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh009: FILE_SCHEMA with non-canonical truncated schema name'),'2;1');\n"
        "FILE_NAME('Lh009.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "/* DEFECT: AUTOMOTIVE_DESIGN_MIM is not a registered schema; _LF suffix is required */\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN_MIM'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('unrecognised-schema-name-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh009(path) -> None:
    Path(path).write_text(_render_lh009())


f.render = _render_lh009  # type: ignore[method-assign]
f.write = _write_lh009    # type: ignore[method-assign]
