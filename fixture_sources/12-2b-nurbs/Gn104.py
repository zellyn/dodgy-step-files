"""Gn104 — trimmed-recursion on B-spline surface.

Catalog claim: "ShapeUpgrade_SplitSurfaceContinuity.Compute recursively
subdivides trimmed B-spline ignoring trim bounds, producing overlapping
sub-patches."

Demonstration: An ADVANCED_FACE whose underlying surface is a
B_SPLINE_SURFACE_WITH_KNOTS trimmed in parameter space such that the
subdivision trigger fires. The face boundary loop covers the middle of the
B-spline parameter domain [0,1]×[0,1] with a 3D trim window at
[0.25,0.75]×[0.25,0.75]. When SplitSurfaceContinuity recurses it ignores
these bounds and subdivides across the full [0,1] domain, generating
overlapping sub-patches.

We use a degree-2, 3-control-point B-spline in each direction with a single
interior knot at 0.5 that triggers the continuity-split branch (C0 junction).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gn104",
             defect="trimmed-recursion: SplitSurfaceContinuity ignores trim bounds on B-spline surface")

# -----------------------------------------------------------------------
# Control point grid (3×3): a flat bilinear patch spanning 1×1 in XY, Z=0
# -----------------------------------------------------------------------
cp00 = f.cartesian_point((0.0, 0.0, 0.0))
cp01 = f.cartesian_point((0.5, 0.0, 0.0))
cp02 = f.cartesian_point((1.0, 0.0, 0.0))
cp10 = f.cartesian_point((0.0, 0.5, 0.0))
cp11 = f.cartesian_point((0.5, 0.5, 0.0))
cp12 = f.cartesian_point((1.0, 0.5, 0.0))
cp20 = f.cartesian_point((0.0, 1.0, 0.0))
cp21 = f.cartesian_point((0.5, 1.0, 0.0))
cp22 = f.cartesian_point((1.0, 1.0, 0.0))

# B_SPLINE_SURFACE_WITH_KNOTS: degree 2 in u and v.
# Knot vector [0,0,0.5,1,1] gives a C0 interior junction at u=v=0.5 that
# triggers ShapeUpgrade_SplitSurfaceContinuity.Compute. The multiplicity
# sequence (1,2,1) encodes: single start, double interior (C0), single end.
# Format: name, u_deg, v_deg, control_points (row-major list of rows),
#   surface_form, u_closed, v_closed, self_intersect,
#   u_multiplicities, v_multiplicities, u_knots, v_knots, knot_spec
bspline_surf = f._emit_raw(
    "B_SPLINE_SURFACE_WITH_KNOTS('bspline_surf',2,2,"
    f"(({cp00.ref()},{cp01.ref()},{cp02.ref()}),"
    f"({cp10.ref()},{cp11.ref()},{cp12.ref()}),"
    f"({cp20.ref()},{cp21.ref()},{cp22.ref()})),"
    ".UNSPECIFIED.,.F.,.F.,.F.,"
    "(1,2,1),(1,2,1),"
    "(0.0,0.5,1.0),(0.0,0.5,1.0),"
    ".UNSPECIFIED.)"
)

# -----------------------------------------------------------------------
# Face boundary: a trimmed rectangle in 3D space at the interior of the
# B-spline domain — u∈[0.25,0.75], v∈[0.25,0.75].
# The B-spline is 1:1 here so 3D corners match parameter corners exactly.
# -----------------------------------------------------------------------
p0 = f.cartesian_point((0.25, 0.25, 0.0))
p1 = f.cartesian_point((0.75, 0.25, 0.0))
p2 = f.cartesian_point((0.75, 0.75, 0.0))
p3 = f.cartesian_point((0.25, 0.75, 0.0))

loop = f.closed_polyline_loop([p0, p1, p2, p3])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], bspline_surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
