"""Gn108 — Init u_min > u_max inverted bounds

Catalog claim: "ShapeUpgrade_SplitSurface.Init silently accepts inverted
bounds (u_min > u_max), producing undefined sub-surfaces."

Demonstration: A B_SPLINE_SURFACE_WITH_KNOTS wrapped in a RECTANGULAR_TRIMMED_SURFACE
with inverted u-bounds: u_min=0.75, u_max=0.25 (u_min > u_max). The API should
reject this or at least explicitly swap them. The defect is that Init silently
accepts the inversion and produces undefined geometric sub-surfaces.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gn108",
             defect="RECTANGULAR_TRIMMED_SURFACE with inverted u bounds (u_min > u_max)")

# Base B-spline surface
cp00 = f.cartesian_point((0.0, 0.0, 0.0))
cp01 = f.cartesian_point((0.0, 1.0, 0.0))
cp10 = f.cartesian_point((1.0, 0.0, 0.0))
cp11 = f.cartesian_point((1.0, 1.0, 0.0))

# Degree-1 (bilinear), 2×2 control points
bspline_base = f._emit_raw(
    "B_SPLINE_SURFACE_WITH_KNOTS('base_bspline',1,1,"
    f"(({cp00.ref()},{cp01.ref()}),"
    f"({cp10.ref()},{cp11.ref()})),"
    ".UNSPECIFIED.,.F.,.F.,.F.,"
    "(1,1),(1,1),"
    "(0.0,1.0),(0.0,1.0),"
    ".UNSPECIFIED.)"
)

# RECTANGULAR_TRIMMED_SURFACE with INVERTED u bounds: u1=0.75, u2=0.25
# u_min > u_max violates the spec but the Init bug silently accepts it
rts = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('inverted_u',{bspline_base.ref()},"
    "0.75,0.25,0.0,1.0,.T.,.T.)"
)

# Face boundary at the expected trimmed region
# (Note: with inverted bounds, this geometry is ill-defined)
p0 = f.cartesian_point((0.25, 0.0, 0.0))
p1 = f.cartesian_point((0.75, 0.0, 0.0))
p2 = f.cartesian_point((0.75, 1.0, 0.0))
p3 = f.cartesian_point((0.25, 1.0, 0.0))

loop = f.closed_polyline_loop([p0, p1, p2, p3])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], rts)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
