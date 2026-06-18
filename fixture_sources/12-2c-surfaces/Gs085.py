"""Gs085 — ShapeUpgrade_SplitSurfaceContinuity.Compute criterion-elevation offset

Catalog claim: "OFFSET_SURFACE wrapping C0 B-spline. Continuity elevation
(C0→C1) applied to base; propagation to offset wrapper missing. Exposes
offset-criterion-elevation branch (line 238 OCCT_HEAL_COVERAGE_V3.md)."

Demonstration: A B_SPLINE_SURFACE_WITH_KNOTS with a C0 interior junction
(knot with multiplicity equal to degree, creating a sharp discontinuity).
This base surface is wrapped in an OFFSET_SURFACE. When continuity elevation
is applied to the base, the offset wrapper should propagate the new elevated
continuity, but the defect is that it doesn't — the offset remains invalid.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gs085",
             defect="OFFSET_SURFACE wrapping C0 B-spline; continuity elevation not propagated to offset")

# Control points for C0 base surface
cp00 = f.cartesian_point((0.0, 0.0, 0.0))
cp01 = f.cartesian_point((0.5, 0.0, 0.0))
cp02 = f.cartesian_point((1.0, 0.0, 0.0))
cp10 = f.cartesian_point((0.0, 0.5, 0.0))
cp11 = f.cartesian_point((0.5, 0.5, 0.5))
cp12 = f.cartesian_point((1.0, 0.5, 0.0))
cp20 = f.cartesian_point((0.0, 1.0, 0.0))
cp21 = f.cartesian_point((0.5, 1.0, 0.0))
cp22 = f.cartesian_point((1.0, 1.0, 0.0))

# C0 B-spline with multiplicity-2 interior knot at u=0.5
# Degree 2, knots [0,0,0.5,1,1] → multiplicities (1,2,1)
bspline_base = f._emit_raw(
    "B_SPLINE_SURFACE_WITH_KNOTS('c0_base',2,2,"
    f"(({cp00.ref()},{cp01.ref()},{cp02.ref()}),"
    f"({cp10.ref()},{cp11.ref()},{cp12.ref()}),"
    f"({cp20.ref()},{cp21.ref()},{cp22.ref()})),"
    ".UNSPECIFIED.,.F.,.F.,.F.,"
    "(1,2,1),(1,1,1),"
    "(0.0,0.5,1.0),(0.0,1.0),"
    ".UNSPECIFIED.)"
)

# Wrap the C0 base in an OFFSET_SURFACE with offset distance 0.1
offset_surf = f._emit_raw(
    f"OFFSET_SURFACE('offset_c0',{bspline_base.ref()},0.1)"
)

# Face boundary covering full domain
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

loop = f.closed_polyline_loop([p0, p1, p2, p3])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], offset_surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
