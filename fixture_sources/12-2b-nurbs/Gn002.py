"""Gn002 — RATIONAL_BSPLINE_CURVE / SURFACE with NbWeights != NbControlPoints.

Catalog claim: a RATIONAL_B_SPLINE_CURVE bears a weights array whose length does
NOT match the control-point list length. STEP semantics require strict equality.
Below the curve carries 4 control points but only 3 weights; the surface variant
carries a 4x4 control net but a 4x3 weights grid (one missing per row).

Byte assertions: contains(b'B_SPLINE_SURFACE'), contains(b'B_SPLINE_CURVE')
Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn002",
    defect=(
        "RATIONAL_B_SPLINE_CURVE: 4 control points but only 3 weights (length mismatch); "
        "RATIONAL_B_SPLINE_SURFACE: 4x4 control net but 4x3 weights grid (column missing); "
        "STEP semantics require strict equality NbWeights == NbControlPoints; "
        "heal: pad weights with 1.0 / truncate to match pole count; warn; do not crash; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Anchor geometry
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Rational BSpline curve — 4 poles, only 3 weights (DEFECT)
c0 = f.cartesian_point((0.0, 0.0, 0.0))
c1 = f.cartesian_point((1.0, 1.0, 0.0))
c2 = f.cartesian_point((2.0, 1.0, 0.0))
c3 = f.cartesian_point((3.0, 0.0, 0.0))

# Complex RATIONAL_B_SPLINE_CURVE entity with 4 poles but only 3 weights
f._emit_raw(
    f"(\n"
    f"  BOUNDED_CURVE()\n"
    f"  B_SPLINE_CURVE(3,(#{c0.eid},#{c1.eid},#{c2.eid},#{c3.eid}),.UNSPECIFIED.,.F.,.F.)\n"
    f"  B_SPLINE_CURVE_WITH_KNOTS((4,4),(0.0,1.0),.UNSPECIFIED.)\n"
    f"  CURVE()\n"
    f"  GEOMETRIC_REPRESENTATION_ITEM()\n"
    f"  RATIONAL_B_SPLINE_CURVE((1.0,2.0,1.0))\n"
    f"  REPRESENTATION_ITEM('rcurve_bad_weights')\n"
    f")"
)

# Rational BSpline surface — 4x4 control net but 4x3 weights grid (DEFECT)
pts = {}
for i in range(4):
    for j in range(4):
        pts[(i,j)] = f.cartesian_point((float(i), float(j), 0.1 * i * j))

def row_refs(i):
    return "(" + ",".join(f"#{pts[(i,j)].eid}" for j in range(4)) + ")"

cp_grid = "(" + ",".join(row_refs(i) for i in range(4)) + ")"

# Only 3 weights per row instead of 4 — the column mismatch defect
def weight_row_3(w):
    return f"({w},{w},{w})"  # 3 weights, not 4

weights_grid = "(" + ",".join(weight_row_3(1.0) for _ in range(4)) + ")"

f._emit_raw(
    f"(\n"
    f"  BOUNDED_SURFACE()\n"
    f"  B_SPLINE_SURFACE(3,3,{cp_grid},.UNSPECIFIED.,.F.,.F.,.F.)\n"
    f"  B_SPLINE_SURFACE_WITH_KNOTS((4,4),(4,4),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)\n"
    f"  GEOMETRIC_REPRESENTATION_ITEM()\n"
    f"  RATIONAL_B_SPLINE_SURFACE({weights_grid})\n"
    f"  REPRESENTATION_ITEM('rsurf_bad_weights')\n"
    f"  SURFACE()\n"
    f")"
)
