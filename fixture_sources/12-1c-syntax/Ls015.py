"""Ls015 — Missing comma between attribute values.

Catalog claim: A list of attributes lacks a comma separator. SFA reports
"Expecting ',', found _3DV instead."

Reproducer recipe: #1=CARTESIAN_POINT('p' (0.,0.,0.));

Byte assertions:
  matches(rb"'[xp]'\\s*\\(")
  matches(rb"'\\w'\\s+\\(")

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls015",
    defect=(
        "Missing comma between attribute values in STEP entity record; "
        "a list of attributes lacks a comma separator; "
        "SFA reports Expecting comma found _3DV instead; "
        "this commonly arises when a generator forgets a trailing comma "
        "after a string literal that immediately precedes an aggregate; "
        "strict reject with precise location diagnostic required; "
        "never silently insert a synthetic comma; "
        "the error message should name the offset of the missing separator "
        "within the parameter list; "
        "defect 1: CARTESIAN_POINT('p' (0.,0.,0.)) missing comma after 'p'; "
        "defect 2: DIRECTION('x' (1.,0.,0.)) missing comma between string and list; "
        "OCC silently accepts with diagnostic but loads empty result; "
        "synonyms: missing comma between STEP attributes, Expecting comma found _3DV, "
        "STEP attribute separator dropped, two attributes adjacent without comma, "
        "comma-less attribute list; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_missing_comma() -> str:
    header = f._render_header()
    return (
        "/* Ls015 - Missing comma between attribute values\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c punctuation\n"
        "   Sources         : S006\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     A list of attributes lacks a comma separator. SFA reports\n"
        "     \"Expecting ',', found _3DV instead.\" This commonly arises when\n"
        "     a generator forgets a trailing comma after a string literal that\n"
        "     immediately precedes an aggregate.\n"
        "   Expected behavior\n"
        "     Strict reject with precise location diagnostic; never silently\n"
        "     insert a synthetic comma. The error message should name the offset\n"
        "     of the missing separator within the parameter list.\n"
        "   ----------------------------------------------------------------------\n"
        "   Reproducer\n"
        "     #1=CARTESIAN_POINT('p' (0.,0.,0.));   <- missing ',' after 'p'\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls015 - missing comma between attribute values'),'2;1');\n"
        "FILE_NAME('Ls015.stp','2026-04-26T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect: missing comma between the 'p' label string and the coord aggregate */\n"
        "#10=CARTESIAN_POINT('p' (0.0,0.0,0.0));\n"
        "/* Defect: missing comma between two scalar attributes */\n"
        "#11=DIRECTION('x' (1.0,0.0,0.0));\n"
        "#20=DIRECTION('x',(1.0,0.0,0.0));\n"
        "#30=AXIS2_PLACEMENT_3D('placement',#10,#20,$);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_missing_comma  # type: ignore[method-assign]
