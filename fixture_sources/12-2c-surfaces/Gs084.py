"""Gs084 — ShapeAnalysis_Surface.IsDegenerated bounded-surface zero-area.

Catalog claim: "RECTANGULAR_TRIMMED_SURFACE with u1==u2 (zero-width trim).
IsDegenerated parameter-difference check fails to detect zero area. Fixture
uses B-spline base with trimmed surface u∈[0,0]."

Demonstration: A B_SPLINE_SURFACE_WITH_KNOTS base surface trimmed by a
RECTANGULAR_TRIMMED_SURFACE with identical u1 and u2 parameters (u1=0.0,
u2=0.0). The parametric domain collapses to a line (zero area in u).
ShapeAnalysis_Surface.IsDegenerated should detect this as degenerate, but
the parameter-difference check fails to catch u1==u2. The face boundary
degenerates to a single line at u=0.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gs084",
             defect="RECTANGULAR_TRIMMED_SURFACE u1==u2 zero-width trim; IsDegenerated fails to detect zero area")

# -----------------------------------------------------------------------
# Base: B_SPLINE_SURFACE_WITH_KNOTS, degree 1, 2×2 control points
# (a simple bilinear ruled surface spanning u,v ∈ [0,1])
# -----------------------------------------------------------------------
cp00 = f.cartesian_point((0.0, 0.0, 0.0))
cp01 = f.cartesian_point((0.0, 1.0, 0.0))
cp10 = f.cartesian_point((1.0, 0.0, 0.0))
cp11 = f.cartesian_point((1.0, 1.0, 0.0))

# Degree-1 B-spline (linear), 2×2 grid, knots [0,1] with mult (1,1)
bspline_base = f._emit_raw(
    "B_SPLINE_SURFACE_WITH_KNOTS('base_bspline',1,1,"
    f"(({cp00.ref()},{cp01.ref()}),"
    f"({cp10.ref()},{cp11.ref()})),"
    ".UNSPECIFIED.,.F.,.F.,.F.,"
    "(1,1),(1,1),"
    "(0.0,1.0),(0.0,1.0),"
    ".UNSPECIFIED.)"
)

# -----------------------------------------------------------------------
# RECTANGULAR_TRIMMED_SURFACE: u1=0.0, u2=0.0 (zero-width!), v1=0.0, v2=1.0
# The trim collapses the u-extent to zero — the surface degenerates to a
# line segment at u=0. IsDegenerated should catch this but doesn't.
# Args: name, basis_surface, u1, u2, v1, v2, usense, vsense
# -----------------------------------------------------------------------
rts = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('trimmed_zero_u',{bspline_base.ref()},"
    "0.0,0.0,0.0,1.0,.T.,.T.)"
)

# -----------------------------------------------------------------------
# Face boundary along the degenerate u=0 line: v ∈ [0,1]
# A degenerate "face" that is just a line at x=0, y ∈ [0,1]
# We build a 1D loop (a degenerate edge collapsing to a line)
# using a single out-and-back oriented edge pair at v=0 and v=1.
# -----------------------------------------------------------------------
p_v0 = f.cartesian_point((0.0, 0.0, 0.0))   # u=0, v=0
p_v1 = f.cartesian_point((0.0, 1.0, 0.0))   # u=0, v=1

# Two vertices
v0 = f.vertex_point(p_v0)
v1 = f.vertex_point(p_v1)

# Forward edge v=0 → v=1
d_fwd = f.direction((0.0, 1.0, 0.0))
vec_fwd = f.vector(d_fwd, 1.0)
line_fwd = f.line(p_v0, vec_fwd)
e_fwd = f.edge_curve(v0, v1, line_fwd)

# Reverse edge v=1 → v=0 (same underlying edge, reversed sense)
loop = f.edge_loop([
    f.oriented_edge(e_fwd, True),
    f.oriented_edge(e_fwd, False),   # degenerate: same edge traversed back
])
fob = f.face_outer_bound(loop)

# The advanced face uses the RECTANGULAR_TRIMMED_SURFACE as its geometry
face = f.advanced_face([fob], rts)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
