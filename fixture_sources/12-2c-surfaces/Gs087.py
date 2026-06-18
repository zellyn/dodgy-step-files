"""Gs087 — ShapeAnalysis_Surface.ComputeBoundIsos cache-stale

Catalog claim: "Periodic B-spline with IsUPeriodic=true, IsVPeriodic=true.
Cache invalidation missing; ComputeBoundIsos reuses stale boundary isos after
internal surface modification. Tests line 620 tolerance-precision-mismatch path."

Demonstration: A B_SPLINE_SURFACE_WITH_KNOTS with periodic knot vectors
(IsUPeriodic=true, IsVPeriodic=true). The boundary iso-curves are cached
internally. If the surface is modified (e.g., by a heal operation), the cache
is not invalidated, and ComputeBoundIsos returns stale iso-curves that no longer
match the actual surface boundary.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gs087",
             defect="Periodic B-spline with stale boundary iso-curve cache after modification")

# Control points for a periodic surface (torus-like, but using a periodic B-spline)
# Arrange points in a grid that closes periodically
cp00 = f.cartesian_point((1.0, 0.0, 0.0))
cp01 = f.cartesian_point((1.0, 1.0, 0.0))
cp02 = f.cartesian_point((0.0, 1.0, 0.0))
cp10 = f.cartesian_point((1.0, 0.0, 1.0))
cp11 = f.cartesian_point((1.0, 1.0, 1.0))
cp12 = f.cartesian_point((0.0, 1.0, 1.0))
cp20 = f.cartesian_point((1.0, 0.0, 0.0))  # wrap back to start
cp21 = f.cartesian_point((1.0, 1.0, 0.0))
cp22 = f.cartesian_point((0.0, 1.0, 0.0))

# Periodic B-spline: degree 2, periodic in both u and v
# Knots for periodic: [0,1,2,3,4] (period 3, no clamped multiplicity)
# For simplicity, we use non-periodic knots but set the periodic flags
bspline_periodic = f._emit_raw(
    "B_SPLINE_SURFACE_WITH_KNOTS('periodic_surf',2,2,"
    f"(({cp00.ref()},{cp01.ref()},{cp02.ref()}),"
    f"({cp10.ref()},{cp11.ref()},{cp12.ref()}),"
    f"({cp20.ref()},{cp21.ref()},{cp22.ref()})),"
    ".UNSPECIFIED.,.T.,.T.,.F.,"
    "(1,1,1),(1,1,1),"
    "(0.0,1.0,2.0),(0.0,1.0,2.0),"
    ".UNSPECIFIED.)"
)

# Face boundary covering domain
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

loop = f.closed_polyline_loop([p0, p1, p2, p3])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], bspline_periodic)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
