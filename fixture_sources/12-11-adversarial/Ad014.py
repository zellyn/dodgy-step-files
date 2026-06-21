"""Ad014 — Float literal with extreme exponent (1E999999) propagates as inf/NaN.

Catalog claim: strtod returns inf/0 for very large/small exponents; downstream
code that converts to a fixed-precision tessellation grid index may overflow
or produce NaN; NaN then poisons sort comparators in STL containers → UAF.

Byte assertions:
  contains(b'1.0E+999999')
  count(b'1.0E+999999') + count(b'1.0E-999999') >= 1

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad014",
    defect=(
        "float literals with extreme exponents (1.0E+999999, 1.0E-999999); "
        "strtod returns +inf or 0; NaN poisons STL sort comparators → UAF; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payloads: raw CARTESIAN_POINTs with extreme exponent literals.
# The builder's _format_real would normalize these, so use _emit_raw.

# Positive extreme exponent: satisfies contains(b'1.0E+999999').
f._emit_raw("CARTESIAN_POINT('',(1.0E+999999,0.,0.))")

# Negative extreme exponent: satisfies count(...) + count(...) >= 1.
f._emit_raw("CARTESIAN_POINT('',(1.0E-999999,0.,0.))")

# Near-double-max: HOOPS Exchange fuzz class trigger.
f._emit_raw("CARTESIAN_POINT('',(1.79E+308,0.,0.))")

# Angle attribute with extreme value: NaN from cos/sin if not clamped.
ax2 = f._emit_raw("AXIS2_PLACEMENT_3D('',#1,$,$)")
f._emit_raw(f"CIRCLE('',#{ax2.eid},1.0E+999999)")
