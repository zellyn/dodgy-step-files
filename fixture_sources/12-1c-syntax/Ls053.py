"""Ls053 — REAL literal in an INTEGER-typed slot (`3.0` where `3` is required).

Catalog claim: ISO 10303-21 distinguishes INTEGER and REAL literals; a REAL
carries a mandatory decimal point. A count/degree/dimension attribute typed
INTEGER in the EXPRESS schema must not receive a REAL literal. This is the
inverse of Ls001 (integer written where a REAL is required). ruststep's
`untyped_parameter` tries `real` before `integer`, so `3.0` in the
`B_SPLINE_CURVE_WITH_KNOTS.degree` slot mis-tokenizes as `Parameter::Real`.

Reproducer recipe:
  #5=B_SPLINE_CURVE_WITH_KNOTS('c',3.0,(#1,#2,#3,#4),.UNSPECIFIED.,.F.,.F.,
      (4,4),(0.,1.),.UNSPECIFIED.);
  -- degree slot is INTEGER; 3.0 is a REAL (fractional-capable) literal

Byte assertions:
  contains(b'B_SPLINE_CURVE_WITH_KNOTS')
  matches(rb"WITH_KNOTS\('c',3\.0,")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a

Pattern-mined from ricosjp/ruststep parameter.rs::untyped_parameter and
issue #56 "tokenize integer as float" (Apache-2.0/MIT — pattern only).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls053",
    defect=(
        "REAL literal in an INTEGER-typed slot; "
        "ISO 10303-21 distinguishes INTEGER and REAL literals, and a REAL "
        "carries a mandatory decimal point; "
        "the B_SPLINE_CURVE_WITH_KNOTS degree attribute is INTEGER in the "
        "EXPRESS schema, but the fixture writes the REAL literal 3.0 where the "
        "integer 3 is required; "
        "this is the inverse of Ls001 (integer written where a REAL is required); "
        "a real-first tokenizer mis-types 3.0 as Parameter::Real; "
        "expected kernel behavior: reject or warn on a non-integral value in an "
        "INTEGER slot; never silently truncate 3.0 to 3; "
        "see also Ls001; "
        "synonyms: REAL where INTEGER expected, degree given 3.0, count field "
        "carries a decimal point, fractional value in integer slot, "
        "float literal in STEP integer attribute; "
        "the B_SPLINE_CURVE_WITH_KNOTS entity is the defect carrier"
    ),
)


def _render_real_in_int_slot() -> str:
    header = f._render_header()
    return (
        "ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('',(1.,1.,0.));\n"
        "#3=CARTESIAN_POINT('',(2.,0.,0.));\n"
        "#4=CARTESIAN_POINT('',(3.,1.,0.));\n"
        "/* Defect: the degree slot of B_SPLINE_CURVE_WITH_KNOTS is INTEGER, but\n"
        "   the REAL literal 3.0 is written where the integer 3 is required. */\n"
        "#5=B_SPLINE_CURVE_WITH_KNOTS('c',3.0,(#1,#2,#3,#4),.UNSPECIFIED.,.F.,.F.,"
        "(4,4),(0.,1.),.UNSPECIFIED.);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_real_in_int_slot  # type: ignore[method-assign]
