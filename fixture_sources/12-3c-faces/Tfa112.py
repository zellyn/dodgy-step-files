"""Tfa112 — ShapeAnalysis_CheckSmallFace.CheckTwisted bspline-saddle.

Catalog claim: Face on B-spline surface with saddle topology (negative Gaussian
curvature); CheckTwisted's normal-direction test confuses positive/negative
curvature regions. The saddle surface (z ≈ x²−y²) has opposite normal
orientation in different (u,v) quadrants. CheckTwisted's scalar-product test
misclassifies this as a twisted/inverted face rather than recognizing legitimate
saddle geometry.

Mechanism: MANIFOLD_SOLID_BREP with a degree-3 B_SPLINE_SURFACE_WITH_KNOTS
approximating a hyperbolic paraboloid z = x²−y² on [−1,1]². A 4×4 control-
point grid (degree 3 in both U and V) captures the sign reversal across the
saddle center. CheckTwisted samples face normals at interior points and detects
the scalar-product sign change, misclassifying the saddle face as twisted.
Companion flat base closes the shell.

Byte assertions:
  - contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa112",
    defect=(
        "CLOSED_SHELL: defect face is B_SPLINE_SURFACE_WITH_KNOTS degree(3,3) 4x4 "
        "control-point grid approximating hyperbolic paraboloid z = x^2-y^2 on [-1,1]^2; "
        "normals flip sign across saddle center (opposite in X vs Y curvature zones); "
        "ShapeAnalysis_CheckSmallFace::CheckTwisted scalar-product test sees sign reversal "
        "and misclassifies saddle face as twisted/inverted; "
        "companion flat base closes shell; defect IS on live CLOSED_SHELL traversal path"
    ),
)

# Degree-3 B-spline surface approximating z = x²−y² on x,y ∈ [−1,1]
# 4×4 control point grid; knots [0,1] with multiplicities [4,4] for clamped
# Domain maps: u ∈ [0,1] → x = 2u−1; v ∈ [0,1] → y = 2v−1
# z values at grid points (i,j): x_i = {-1, -1/3, 1/3, 1}, y_j = {-1, -1/3, 1/3, 1}
# z = x²−y² at each grid point

xs = [-1.0, -1.0/3.0, 1.0/3.0, 1.0]
ys = [-1.0, -1.0/3.0, 1.0/3.0, 1.0]

cp = []
for x in xs:
    row = []
    for y in ys:
        z = x*x - y*y
        row.append(f.cartesian_point((x, y, z)))
    cp.append(row)

saddle_surf = f.b_spline_surface_with_knots(
    u_degree=3, v_degree=3,
    control_points_grid=cp,
    u_multiplicities=[4, 4],
    v_multiplicities=[4, 4],
    u_knots=[0.0, 1.0],
    v_knots=[0.0, 1.0],
)

# Corner points of the saddle boundary (at corners of [−1,1]²)
# z at corners: (-1,-1)→0, (1,-1)→0, (1,1)→0, (-1,1)→0
# z at mid-edges varies; at corners it's x²−y² = 1−1 = 0
C00 = (-1.0, -1.0, 0.0)   # x=-1, y=-1: z = 1-1 = 0
C10 = ( 1.0, -1.0, 0.0)   # x= 1, y=-1: z = 1-1 = 0
C11 = ( 1.0,  1.0, 0.0)   # x= 1, y= 1: z = 1-1 = 0
C01 = (-1.0,  1.0, 0.0)   # x=-1, y= 1: z = 1-1 = 0

p00 = f.cartesian_point(C00); p10 = f.cartesian_point(C10)
p11 = f.cartesian_point(C11); p01 = f.cartesian_point(C01)
v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)

def straight_edge(va, ca, vb, cb):
    dx = cb[0]-ca[0]; dy = cb[1]-ca[1]; dz = cb[2]-ca[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    d = f.direction((dx/mag, dy/mag, dz/mag))
    return f.edge_curve(va, vb, f.line(f.cartesian_point(ca), f.vector(d, mag)))

e_s  = straight_edge(v00, C00, v10, C10)   # south: x:-1→1, y=-1
e_e  = straight_edge(v10, C10, v11, C11)   # east:  y:-1→1, x= 1
e_n  = straight_edge(v11, C11, v01, C01)   # north: x:1→-1, y= 1
e_w  = straight_edge(v01, C01, v00, C00)   # west:  y:1→-1, x=-1

saddle_loop = f.edge_loop([
    f.oriented_edge(e_s, True), f.oriented_edge(e_e, True),
    f.oriented_edge(e_n, True), f.oriented_edge(e_w, True),
])
face_saddle = f.advanced_face([f.face_outer_bound(saddle_loop)], saddle_surf)

# Companion flat base at z=-1.5 to close the shell
Cb00 = (-1.0, -1.0, -1.5); Cb10 = (1.0, -1.0, -1.5)
Cb11 = (1.0,  1.0, -1.5);  Cb01 = (-1.0, 1.0, -1.5)
pb00 = f.cartesian_point(Cb00); pb10 = f.cartesian_point(Cb10)
pb11 = f.cartesian_point(Cb11); pb01 = f.cartesian_point(Cb01)
vb00 = f.vertex_point(pb00); vb10 = f.vertex_point(pb10)
vb11 = f.vertex_point(pb11); vb01 = f.vertex_point(pb01)

eb0 = straight_edge(vb00, Cb00, vb10, Cb10)
eb1 = straight_edge(vb10, Cb10, vb11, Cb11)
eb2 = straight_edge(vb11, Cb11, vb01, Cb01)
eb3 = straight_edge(vb01, Cb01, vb00, Cb00)

bot_loop = f.edge_loop([
    f.oriented_edge(eb0, True), f.oriented_edge(eb1, True),
    f.oriented_edge(eb2, True), f.oriented_edge(eb3, True),
])
face_bot = f.advanced_face([f.face_outer_bound(bot_loop)], f.plane(
    f.axis2_placement_3d(pb00, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))))

# Vertical connecting edges
ev00 = straight_edge(v00, C00, vb00, Cb00)
ev10 = straight_edge(v10, C10, vb10, Cb10)
ev11 = straight_edge(v11, C11, vb11, Cb11)
ev01 = straight_edge(v01, C01, vb01, Cb01)

# South wall (y=-1)
sw_loop = f.edge_loop([
    f.oriented_edge(e_s, True), f.oriented_edge(ev10, True),
    f.oriented_edge(eb0, False), f.oriented_edge(ev00, False),
])
face_sw = f.advanced_face([f.face_outer_bound(sw_loop)], f.plane(
    f.axis2_placement_3d(pb00, f.direction((0.0, -1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))))

# East wall (x=1)
ew_loop = f.edge_loop([
    f.oriented_edge(e_e, True), f.oriented_edge(ev11, True),
    f.oriented_edge(eb1, False), f.oriented_edge(ev10, False),
])
face_ew = f.advanced_face([f.face_outer_bound(ew_loop)], f.plane(
    f.axis2_placement_3d(pb10, f.direction((1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))))

# North wall (y=1)
nw_loop = f.edge_loop([
    f.oriented_edge(ev01, True), f.oriented_edge(e_n, False),
    f.oriented_edge(ev11, False), f.oriented_edge(eb2, False),
])
face_nw = f.advanced_face([f.face_outer_bound(nw_loop)], f.plane(
    f.axis2_placement_3d(pb01, f.direction((0.0, 1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))))

# West wall (x=-1)
ww_loop = f.edge_loop([
    f.oriented_edge(ev00, True), f.oriented_edge(e_w, False),
    f.oriented_edge(ev01, False), f.oriented_edge(eb3, False),
])
face_ww = f.advanced_face([f.face_outer_bound(ww_loop)], f.plane(
    f.axis2_placement_3d(pb00, f.direction((-1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))))

# ── CLOSED_SHELL → MANIFOLD_SOLID_BREP ──────────────────────────────────────────
closed_sh = f.closed_shell([face_saddle, face_bot, face_sw, face_ew, face_nw, face_ww])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa112.stp")
