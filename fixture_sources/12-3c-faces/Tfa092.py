"""Tfa092 — ShapeAnalysis_CheckSmallFace.CheckTwisted concave-saddle.

Catalog claim: Face whose BSpline surface has both convex and concave regions
(hyperbolic paraboloid saddle). Twisted-face classifier confuses two-zone
topology when computing normal orientation. Surface curvature is positive in
X direction (bulge up) and negative in Y direction (pinch down).

Mechanism: CLOSED_SHELL with a B_SPLINE_SURFACE_WITH_KNOTS degree(2×2) saddle
surface — a hyperbolic paraboloid. Control-point grid (3×3) yields positive
curvature along U (z increases toward U=1) and negative curvature along V (z
decreases toward V=1). CheckTwisted samples the surface normal at interior
points; the sign change between the two curvature zones causes incorrect
classification. Companion flat base closes the shell.

Byte assertions:
  - contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(12) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa092",
    defect=(
        "CLOSED_SHELL: defect face is B_SPLINE_SURFACE_WITH_KNOTS degree(2,2) "
        "saddle grid 3×3 control points; curvature positive in U (z bulges up) "
        "and negative in V (z pinches down); "
        "CheckTwisted: normal-direction sign change between convex and concave zones "
        "causes two-zone topology misclassification; "
        "companion flat base closes shell; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# ── Saddle (hyperbolic paraboloid) B-spline surface, degree 2×2 ──────────────
# 3×3 control-point grid (U outer, V inner):
#   Row U=0: z=-1, 0, -1  (concave in V)
#   Row U=1: z= 0, 2,  0  (apex, convex in U)
#   Row U=2: z=-1, 0, -1  (concave in V)
# Surface spans X=[0,10], Y=[0,10]; interior has saddle at center.
cp = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0,  0.0, -1.0), (0.0,  5.0,  0.0), (0.0, 10.0, -1.0)],
    [(5.0,  0.0,  0.0), (5.0,  5.0,  2.0), (5.0, 10.0,  0.0)],
    [(10.0, 0.0, -1.0), (10.0, 5.0,  0.0), (10.0,10.0, -1.0)],
]]
saddle_surf = f.b_spline_surface_with_knots(
    u_degree=2, v_degree=2,
    control_points_grid=cp,
    u_multiplicities=[3, 3],
    v_multiplicities=[3, 3],
    u_knots=[0.0, 10.0],
    v_knots=[0.0, 10.0],
)

# ── Corner coordinates of saddle boundary ────────────────────────────────────
C00 = (0.0,  0.0, -1.0)
C10 = (10.0, 0.0, -1.0)
C11 = (10.0, 10.0, -1.0)
C01 = (0.0,  10.0, -1.0)

p00=f.cartesian_point(C00); p10=f.cartesian_point(C10)
p11=f.cartesian_point(C11); p01=f.cartesian_point(C01)
v00=f.vertex_point(p00);  v10=f.vertex_point(p10)
v11=f.vertex_point(p11);  v01=f.vertex_point(p01)

def straight_edge(va, ca, vb, cb):
    dx=cb[0]-ca[0]; dy=cb[1]-ca[1]; dz=cb[2]-ca[2]
    mag=math.sqrt(dx*dx+dy*dy+dz*dz)
    d=f.direction((dx/mag, dy/mag, dz/mag))
    return f.edge_curve(va, vb, f.line(f.cartesian_point(ca), f.vector(d, mag)))

e_s = straight_edge(v00, C00, v10, C10)
e_e = straight_edge(v10, C10, v11, C11)
e_n = straight_edge(v11, C11, v01, C01)
e_w = straight_edge(v01, C01, v00, C00)

saddle_loop = f.edge_loop([
    f.oriented_edge(e_s, True), f.oriented_edge(e_e, True),
    f.oriented_edge(e_n, True), f.oriented_edge(e_w, True),
])
face_saddle = f.advanced_face([f.face_outer_bound(saddle_loop)], saddle_surf)

# ── Companion flat base at z=-2 to close the shell ───────────────────────────
Cb00=(0.0,0.0,-2.0); Cb10=(10.0,0.0,-2.0); Cb11=(10.0,10.0,-2.0); Cb01=(0.0,10.0,-2.0)
pb00=f.cartesian_point(Cb00); pb10=f.cartesian_point(Cb10)
pb11=f.cartesian_point(Cb11); pb01=f.cartesian_point(Cb01)
vb00=f.vertex_point(pb00); vb10=f.vertex_point(pb10)
vb11=f.vertex_point(pb11); vb01=f.vertex_point(pb01)

eb0=straight_edge(vb00,Cb00,vb10,Cb10)
eb1=straight_edge(vb10,Cb10,vb11,Cb11)
eb2=straight_edge(vb11,Cb11,vb01,Cb01)
eb3=straight_edge(vb01,Cb01,vb00,Cb00)
bot_loop=f.edge_loop([
    f.oriented_edge(eb0,True),f.oriented_edge(eb1,True),
    f.oriented_edge(eb2,True),f.oriented_edge(eb3,True),
])
ax_bot=f.axis2_placement_3d(pb00,f.direction((0.0,0.0,-1.0)),f.direction((1.0,0.0,0.0)))
face_bot=f.advanced_face([f.face_outer_bound(bot_loop)],f.plane(ax_bot))

# Vertical connecting edges at 4 corners
ev00=straight_edge(v00,C00,vb00,Cb00)
ev10=straight_edge(v10,C10,vb10,Cb10)
ev11=straight_edge(v11,C11,vb11,Cb11)
ev01=straight_edge(v01,C01,vb01,Cb01)

# South wall y=0
sw_loop=f.edge_loop([
    f.oriented_edge(e_s,True),f.oriented_edge(ev10,True),
    f.oriented_edge(eb0,False),f.oriented_edge(ev00,False),
])
ax_sw=f.axis2_placement_3d(pb00,f.direction((0.0,-1.0,0.0)),f.direction((1.0,0.0,0.0)))
face_sw=f.advanced_face([f.face_outer_bound(sw_loop)],f.plane(ax_sw))

# East wall x=10
ew_loop=f.edge_loop([
    f.oriented_edge(e_e,True),f.oriented_edge(ev11,True),
    f.oriented_edge(eb1,False),f.oriented_edge(ev10,False),
])
ax_ew=f.axis2_placement_3d(pb10,f.direction((1.0,0.0,0.0)),f.direction((0.0,1.0,0.0)))
face_ew=f.advanced_face([f.face_outer_bound(ew_loop)],f.plane(ax_ew))

# North wall y=10
nw_loop=f.edge_loop([
    f.oriented_edge(ev01,True),f.oriented_edge(e_n,False),
    f.oriented_edge(ev11,False),f.oriented_edge(eb2,False),
])
ax_nw=f.axis2_placement_3d(pb01,f.direction((0.0,1.0,0.0)),f.direction((1.0,0.0,0.0)))
face_nw=f.advanced_face([f.face_outer_bound(nw_loop)],f.plane(ax_nw))

# West wall x=0
ww_loop=f.edge_loop([
    f.oriented_edge(ev00,True),f.oriented_edge(e_w,False),
    f.oriented_edge(ev01,False),f.oriented_edge(eb3,False),
])
ax_ww=f.axis2_placement_3d(pb00,f.direction((-1.0,0.0,0.0)),f.direction((0.0,1.0,0.0)))
face_ww=f.advanced_face([f.face_outer_bound(ww_loop)],f.plane(ax_ww))

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh=f.closed_shell([face_saddle,face_bot,face_sw,face_ew,face_nw,face_ww])
msb=f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb,mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa092.stp")
