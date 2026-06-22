"""Le048 — REAL literal exceeding double range (overflow → +Inf / underflow → 0).

Catalog claim: ISO 10303-21 REAL has no syntactic form for non-finite
values. Producers serialising via printf %g may emit 1.0E+999 (overflows
to +Inf) or 1.0E-999 (underflows to 0). A receiver must reject or snap,
not let +Inf or -Inf enter the geometric pipeline.

Reproducer recipe:
  CARTESIAN_POINT('overflow',(1.0E+999,0.0,0.0))
  CARTESIAN_POINT('underflow',(1.0E-999,0.0,0.0))

Byte assertions:
  contains(b'1.0E+999') or contains(b'1.0E-999')
  matches(rb'1\\.0E[+-]999')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le048",
    defect=(
        "REAL literal exceeding double range: overflow → +Inf / underflow → 0; "
        "ISO 10303-21 Ed.3 §6.4.5: REAL has no infinity form (no +Inf, -Inf, NaN); "
        "producers internally holding IEEE-754 doubles and serialising via printf %g "
        "may emit 1.0E+999 (overflows to +Inf on parse) "
        "or 1.0E-999 (underflows to 0 on parse); "
        "receiver must detect overflow during literal-to-binary conversion and reject; "
        "must not let +Inf or -Inf enter the geometric pipeline; "
        "defect 1: CARTESIAN_POINT with X=1.0E+999 (overflows to IEEE-754 +Inf); "
        "defect 2: CARTESIAN_POINT with X=1.0E-999 (underflows to 0); "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: inject CARTESIAN_POINT entities with out-of-range REAL
# literals. These values are injected as raw STEP text to preserve the
# exact bytes 1.0E+999 and 1.0E-999 (which cannot be produced by the
# builder's _format_real since Python float would represent them as inf/0).
#
# #8998: overflow — 1.0E+999 (exponent 999 exceeds IEEE-754 double max ~308)
# #8999: underflow — 1.0E-999 (exponent -999 underflows to denormal/zero)
#
# Satisfies:
#   contains(b'1.0E+999')            — #8998
#   contains(b'1.0E-999')            — #8999
#   matches(rb'1\.0E[+-]999')        — both entities

_original_render = f.render


def _render_with_out_of_range_reals() -> str:
    text = _original_render()
    oor_lines = (
        "#8998=CARTESIAN_POINT('overflow',(1.0E+999,0.0,0.0));\n"
        "#8999=CARTESIAN_POINT('underflow',(1.0E-999,0.0,0.0));\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + oor_lines + text[idx:]


f.render = _render_with_out_of_range_reals  # type: ignore[method-assign]
