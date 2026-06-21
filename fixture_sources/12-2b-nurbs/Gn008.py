"""Gn008 — High-curvature curves: knot multiplicity at full degree producing near-cusps.

Catalog claim: BSpline curves with multi-knots at full-degree multiplicity (cusp-
producing) or rational BSpline with control-point weight ratio above ~1e3 cause
downstream meshers to over-resolve or fail.

Byte assertion: contains(b'B_SPLINE_CURVE')
Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn008",
    defect=(
        "High-curvature B-spline curves: "
        "(A) B_SPLINE_CURVE_WITH_KNOTS degree 3 with interior knot of multiplicity 3 "
        "(full degree = cusp-producing near-cusp); "
        "(B) RATIONAL_B_SPLINE_CURVE with weights (1,1000,1,1) — ratio ~1e3 causes "
        "mesher over-resolution or failure; "
        "accept geometrically; flag as quality warning; downstream meshers must detect "
        "and refuse/refit before meshing; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Anchor
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# (A) Degree-3 B-spline with interior knot multiplicity 3 (= full degree = cusp)
# 7 control points; knots (0,0,0,0, 0.5,0.5,0.5, 1,1,1,1) — full mult at 0.5
a_pts = [
    f.cartesian_point((0.0,  0.0, 0.0)),
    f.cartesian_point((0.5,  1.0, 0.0)),
    f.cartesian_point((1.0,  2.0, 0.0)),  # approaching cusp
    f.cartesian_point((1.5,  0.0, 0.0)),  # C0 break (cusp) at t=0.5
    f.cartesian_point((2.0, -1.0, 0.0)),
    f.cartesian_point((2.5,  0.5, 0.0)),
    f.cartesian_point((3.0,  0.0, 0.0)),
]
a_refs = "(" + ",".join(f"#{p.eid}" for p in a_pts) + ")"
f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('cusp_mult3',3,"
    f"{a_refs},.UNSPECIFIED.,.F.,.F.,"
    f"(4,3,4),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# (B) Rational B-spline with extreme weight ratio: weights (1,1000,1,1)
b_pts = [
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.cartesian_point((1.0, 2.0, 0.0)),
    f.cartesian_point((2.0, 2.0, 0.0)),
    f.cartesian_point((3.0, 0.0, 0.0)),
]
b_refs = "(" + ",".join(f"#{p.eid}" for p in b_pts) + ")"
f._emit_raw(
    f"(\n"
    f"  BOUNDED_CURVE()\n"
    f"  B_SPLINE_CURVE(3,{b_refs},.UNSPECIFIED.,.F.,.F.)\n"
    f"  B_SPLINE_CURVE_WITH_KNOTS((4,4),(0.0,1.0),.UNSPECIFIED.)\n"
    f"  CURVE()\n"
    f"  GEOMETRIC_REPRESENTATION_ITEM()\n"
    f"  RATIONAL_B_SPLINE_CURVE((1.0,1000.0,1.0,1.0))\n"
    f"  REPRESENTATION_ITEM('high_weight_ratio')\n"
    f")"
)
