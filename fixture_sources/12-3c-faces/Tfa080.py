"""Tfa080 — CheckTwisted normal-inversion (saddle surface).

Catalog claim: B-spline surface with hyperbolic (saddle) geometry. Surface
normal flips sign at (u=0.5, v=0.5) interior point due to sign-change in
Gaussian curvature. Face boundary rectangular but interior normal inversion
indicates saddle twist where curvature changes sign.

Mechanism: CLOSED_SHELL. The defect face uses a B_SPLINE_SURFACE_WITH_KNOTS
whose control-point grid forms a hyperbolic paraboloid (saddle): corners at
z=+2 (00, 11) and z=-2 (10, 01). The normal flips sign across the saddle
surface interior. ShapeAnalysis_CheckSmallFace::CheckTwisted detects the
inversion via scalar product < 0 at interior sample point (u=0.5, v=0.5).

Byte assertions:
  - contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa080",
    defect=(
        "CLOSED_SHELL: defect face is B_SPLINE_SURFACE_WITH_KNOTS degree(1,1) "
        "saddle grid — corners (0,0,+2),(10,0,-2),(0,10,-2),(10,10,+2); "
        "Gaussian curvature negative everywhere; surface normal flips sign at "
        "(u=0.5,v=0.5) interior point; scalar product < 0; "
        "CheckTwisted flags normal inversion; "
        "companion flat faces close shell; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# ── Saddle (hyperbolic paraboloid) B-spline surface, degree 1×1 ──────────────
# 2×2 control-point grid (outer index U, inner index V):
#   U=0: (0,0,+2), (0,10,-2)
#   U=1: (10,0,-2), (10,10,+2)
cp = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0, 0.0, 2.0), (0.0, 10.0, -2.0)],
    [(10.0, 0.0, -2.0), (10.0, 10.0, 2.0)],
]]
saddle_surf = f.b_spline_surface_with_knots(
    u_degree=1, v_degree=1,
    control_points_grid=cp,
    u_multiplicities=[2, 2],
    v_multiplicities=[2, 2],
    u_knots=[0.0, 10.0],
    v_knots=[0.0, 10.0],
)

# ── Saddle corner coordinates ─────────────────────────────────────────────────
C00 = (0.0,  0.0,  2.0)
C10 = (10.0, 0.0, -2.0)
C11 = (10.0, 10.0, 2.0)
C01 = (0.0,  10.0, -2.0)

p00 = f.cartesian_point(C00); p10 = f.cartesian_point(C10)
p11 = f.cartesian_point(C11); p01 = f.cartesian_point(C01)
v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)

def straight_edge(f, va, ca, vb, cb):
    dx=cb[0]-ca[0]; dy=cb[1]-ca[1]; dz=cb[2]-ca[2]
    mag=math.sqrt(dx*dx+dy*dy+dz*dz)
    d=f.direction((dx/mag, dy/mag, dz/mag))
    return f.edge_curve(va, vb, f.line(f.cartesian_point(ca), f.vector(d, mag)))

e_s = straight_edge(f, v00, C00, v10, C10)
e_e = straight_edge(f, v10, C10, v11, C11)
e_n = straight_edge(f, v11, C11, v01, C01)
e_w = straight_edge(f, v01, C01, v00, C00)

saddle_loop = f.edge_loop([
    f.oriented_edge(e_s, True), f.oriented_edge(e_e, True),
    f.oriented_edge(e_n, True), f.oriented_edge(e_w, True),
])
face_saddle = f.advanced_face([f.face_outer_bound(saddle_loop)], saddle_surf)

# ── Companion flat base to close the shell ────────────────────────────────────
# Flat square base at z=-3, 10×10
B = (0.0, 0.0, -3.0)
pb00 = f.cartesian_point((0.0,  0.0,  -3.0))
pb10 = f.cartesian_point((10.0, 0.0,  -3.0))
pb11 = f.cartesian_point((10.0, 10.0, -3.0))
pb01 = f.cartesian_point((0.0,  10.0, -3.0))
vb00=f.vertex_point(pb00); vb10=f.vertex_point(pb10)
vb11=f.vertex_point(pb11); vb01=f.vertex_point(pb01)

Cb00=(0.0,0.0,-3.0); Cb10=(10.0,0.0,-3.0); Cb11=(10.0,10.0,-3.0); Cb01=(0.0,10.0,-3.0)

eb0 = straight_edge(f, vb00, Cb00, vb10, Cb10)
eb1 = straight_edge(f, vb10, Cb10, vb11, Cb11)
eb2 = straight_edge(f, vb11, Cb11, vb01, Cb01)
eb3 = straight_edge(f, vb01, Cb01, vb00, Cb00)
bot_loop = f.edge_loop([
    f.oriented_edge(eb0, True), f.oriented_edge(eb1, True),
    f.oriented_edge(eb2, True), f.oriented_edge(eb3, True),
])
ax_bot = f.axis2_placement_3d(pb00, f.direction((0.0,0.0,-1.0)), f.direction((1.0,0.0,0.0)))
face_bot = f.advanced_face([f.face_outer_bound(bot_loop)], f.plane(ax_bot))

# Vertical (skewed) connecting edges at 4 corners
ev00 = straight_edge(f, v00, C00, vb00, Cb00)
ev10 = straight_edge(f, v10, C10, vb10, Cb10)
ev11 = straight_edge(f, v11, C11, vb11, Cb11)
ev01 = straight_edge(f, v01, C01, vb01, Cb01)

# South wall y=0
sw_loop = f.edge_loop([
    f.oriented_edge(e_s, True), f.oriented_edge(ev10, True),
    f.oriented_edge(eb0, False), f.oriented_edge(ev00, False),
])
ax_sw = f.axis2_placement_3d(pb00, f.direction((0.0,-1.0,0.0)), f.direction((1.0,0.0,0.0)))
face_sw = f.advanced_face([f.face_outer_bound(sw_loop)], f.plane(ax_sw))

# East wall x=10
ew_loop = f.edge_loop([
    f.oriented_edge(e_e, True), f.oriented_edge(ev11, True),
    f.oriented_edge(eb1, False), f.oriented_edge(ev10, False),
])
ax_ew = f.axis2_placement_3d(pb10, f.direction((1.0,0.0,0.0)), f.direction((0.0,1.0,0.0)))
face_ew = f.advanced_face([f.face_outer_bound(ew_loop)], f.plane(ax_ew))

# North wall y=10
nw_loop = f.edge_loop([
    f.oriented_edge(ev01, True), f.oriented_edge(e_n, False),
    f.oriented_edge(ev11, False), f.oriented_edge(eb2, False),
])
ax_nw = f.axis2_placement_3d(pb01, f.direction((0.0,1.0,0.0)), f.direction((1.0,0.0,0.0)))
face_nw = f.advanced_face([f.face_outer_bound(nw_loop)], f.plane(ax_nw))

# West wall x=0
ww_loop = f.edge_loop([
    f.oriented_edge(ev00, True), f.oriented_edge(e_w, False),
    f.oriented_edge(ev01, False), f.oriented_edge(eb3, False),
])
ax_ww = f.axis2_placement_3d(pb00, f.direction((-1.0,0.0,0.0)), f.direction((0.0,1.0,0.0)))
face_ww = f.advanced_face([f.face_outer_bound(ww_loop)], f.plane(ax_ww))

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face_saddle, face_bot, face_sw, face_ew, face_nw, face_ww])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa080.stp")
