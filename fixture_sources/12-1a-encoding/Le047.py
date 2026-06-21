"""Le047 — REAL literal at IEEE-754 subnormal / minimum-normal / maximum boundaries.

Catalog claim: ISO 10303-21 specifies REAL as decimal floating-point but
most implementations parse into IEEE-754 binary64. Inputs at the subnormal
boundary test for two failure modes: readers that round to zero and silently
drop the value, and readers that flag underflow and reject the file.

Reproducer recipe:
  CARTESIAN_POINT('subnormal',(4.9406564584124654E-324,0.0,0.0))
  CARTESIAN_POINT('min-normal',(2.2250738585072014E-308,0.0,0.0))
  CARTESIAN_POINT('max-finite',(1.7976931348623157E+308,0.0,0.0))
  negative zero: -0.0

Byte assertions:
  contains(b'4.9406564584124654E-324') or contains(b'2.2250738585072014E-308') or contains(b'-0.0')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le047",
    defect=(
        "REAL literal at IEEE-754 subnormal / minimum-normal / maximum boundaries; "
        "ISO 10303-21 Ed.3 §6.4.5: REAL is decimal floating-point; "
        "most implementations parse into IEEE-754 binary64; "
        "subnormal: 4.9406564584124654E-324 (smallest positive subnormal double); "
        "min-normal: 2.2250738585072014E-308 (smallest positive normal double); "
        "max-finite: 1.7976931348623157E+308 (largest finite double); "
        "negative zero: -0.0 (IEEE-754 negative zero); "
        "failure mode 1: reader rounds subnormal to zero and silently drops the value; "
        "failure mode 2: reader flags underflow and rejects the file; "
        "A coordinate at this magnitude arises in BSpline weight values from buggy producers; "
        "heal and accept: parse value losslessly; snap below-precision values to zero with diagnostic; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: inject CARTESIAN_POINT entities whose coordinate values sit
# at IEEE-754 double-precision boundaries. These values are injected as raw
# STEP text to preserve exact byte representation (the builder's _format_real
# would snap near-zero values).
#
# #8996: subnormal — 4.9406564584124654E-324 (smallest positive subnormal)
# #8997: min-normal — 2.2250738585072014E-308 (smallest positive normal)
# #8998: max-finite — 1.7976931348623157E+308 (largest finite double)
# #8999: negative zero — -0.0 (IEEE-754 signed zero)
#
# Satisfies:
#   contains(b'4.9406564584124654E-324')  — #8996
#   contains(b'2.2250738585072014E-308')  — #8997
#   contains(b'-0.0')                     — #8999

_original_render = f.render


def _render_with_ieee754_boundary_reals() -> str:
    text = _original_render()
    boundary_lines = (
        "#8996=CARTESIAN_POINT('subnormal',(4.9406564584124654E-324,0.0,0.0));\n"
        "#8997=CARTESIAN_POINT('min-normal',(2.2250738585072014E-308,0.0,0.0));\n"
        "#8998=CARTESIAN_POINT('max-finite',(1.7976931348623157E+308,0.0,0.0));\n"
        "#8999=CARTESIAN_POINT('negative-zero',(-0.0,0.0,0.0));\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + boundary_lines + text[idx:]


f.render = _render_with_ieee754_boundary_reals  # type: ignore[method-assign]
