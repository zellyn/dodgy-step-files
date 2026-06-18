"""Gn106 — B-spline-of-Bezier conversion bloat

Catalog claim: "ShapeUpgrade_ConvertSurfaceToBezierBasis converts
single-Bezier B-spline into multiple Bezier patches when direct passthrough
would suffice."

Demonstration: A B_SPLINE_SURFACE_WITH_KNOTS that is already a single Bezier
patch (degree 2 in each direction, 3×3 control points, knots [0,0,0,1,1,1] in
both u and v). Conversion to Bezier basis should recognize this as already
complete Bezier and pass it through unchanged. The defect is that the conversion
algorithm subdivides it into multiple smaller patches unnecessarily, causing bloat.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gn106",
             defect="B-spline that is single Bezier patch bloats on conversion to Bezier basis")

# Control point grid 3×3 forming a simple bilinear patch
cp00 = f.cartesian_point((0.0, 0.0, 0.0))
cp01 = f.cartesian_point((0.5, 0.0, 0.0))
cp02 = f.cartesian_point((1.0, 0.0, 0.0))
cp10 = f.cartesian_point((0.0, 0.5, 0.0))
cp11 = f.cartesian_point((0.5, 0.5, 0.5))
cp12 = f.cartesian_point((1.0, 0.5, 0.0))
cp20 = f.cartesian_point((0.0, 1.0, 0.0))
cp21 = f.cartesian_point((0.5, 1.0, 0.0))
cp22 = f.cartesian_point((1.0, 1.0, 0.0))

# Single-Bezier B-spline surface: degree 2, 3×3 CP, knots [0,0,0,1,1,1]
# This is already in Bezier form but the defect is that conversion incorrectly
# subdivides it.
bspline_surf = f._emit_raw(
    "B_SPLINE_SURFACE_WITH_KNOTS('single_bezier',"
    "2,2,"
    f"(({cp00.ref()},{cp01.ref()},{cp02.ref()}),"
    f"({cp10.ref()},{cp11.ref()},{cp12.ref()}),"
    f"({cp20.ref()},{cp21.ref()},{cp22.ref()})),"
    ".UNSPECIFIED.,.F.,.F.,.F.,"
    "(1,1,1),(1,1,1),"
    "(0.0,1.0),(0.0,1.0),"
    ".UNSPECIFIED.)"
)

# Face boundary: full domain [0,1]×[0,1]
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

loop = f.closed_polyline_loop([p0, p1, p2, p3])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], bspline_surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
