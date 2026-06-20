"""Tfa079 — CheckSplittingVertices vertex-on-edge midspan.

Catalog claim: Planar face with T-vertex configuration: vertex at midpoint
(50, 0) of edge from (0,0) to (100,0). Second inner loop with vertices at
(50, -50), (50, -30), (50, -70) creates vertex-on-edge pattern.

Mechanism: CLOSED_SHELL box (100×100×1 mm). The top face (z=1) is a PLANE.
The bottom face (z=0) has an outer wire with an extra vertex at (50,0,0)
which sits exactly on the midpoint of the outer edge from (0,0,0) to
(100,0,0). A second inner wire uses (50,0,0) as its northmost vertex and
extends down into the face to form a T-junction with a vertex exactly on the
outer boundary edge. ShapeAnalysis_CheckSplittingVertices should detect the
vertex at t=0.5 on the outer edge.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(14) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa079",
    defect=(
        "CLOSED_SHELL 100×100×1 mm box; bottom face (z=0) outer wire has T-vertex "
        "at midpoint (50,0,0) of bottom edge; inner FACE_BOUND triangle uses vertex "
        "at (50,0,0) as apex, touching outer boundary mid-edge; "
        "CheckSplittingVertices: vertex at parameter t=0.5 on edge e_s lies on "
        "outer boundary; projection distance near-zero; "
        "splitting vertex count > 0; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

W = 100.0
H = 1.0

# ── Vertices of outer box ────────────────────────────────────────────────────
# Bottom z=0: split outer edge at (50,0,0) to embed T-vertex
p_s0   = f.cartesian_point((0.0,  0.0, 0.0))   # bottom-left
p_smid = f.cartesian_point((50.0, 0.0, 0.0))   # T-vertex midpoint of south edge
p_s1   = f.cartesian_point((W,    0.0, 0.0))   # bottom-right
p_e    = f.cartesian_point((W,    W,   0.0))   # top-right
p_n    = f.cartesian_point((0.0,  W,   0.0))   # top-left (north-west)

vs0   = f.vertex_point(p_s0)
vsmid = f.vertex_point(p_smid)
vs1   = f.vertex_point(p_s1)
ve    = f.vertex_point(p_e)
vn    = f.vertex_point(p_n)

# Bottom outer wire: 5 edges (south split into two halves, then E, N, W)
e_sw = f.edge_curve(vs0, vsmid, f.line(p_s0, f.vector(f.direction((1.0, 0.0, 0.0)), 50.0)))
e_se = f.edge_curve(vsmid, vs1,  f.line(p_smid, f.vector(f.direction((1.0, 0.0, 0.0)), 50.0)))
e_e  = f.edge_curve(vs1, ve,     f.line(p_s1,  f.vector(f.direction((0.0, 1.0, 0.0)), W)))
e_n  = f.edge_curve(ve,  vn,     f.line(p_e,   f.vector(f.direction((-1.0, 0.0, 0.0)), W)))
e_w  = f.edge_curve(vn,  vs0,    f.line(p_n,   f.vector(f.direction((0.0, -1.0, 0.0)), W)))

bot_outer_loop = f.edge_loop([
    f.oriented_edge(e_sw, True), f.oriented_edge(e_se, True),
    f.oriented_edge(e_e,  True), f.oriented_edge(e_n,  True),
    f.oriented_edge(e_w,  True),
])
bot_outer_fob = f.face_outer_bound(bot_outer_loop)

# Inner T-wire: triangle pointing down from T-vertex at (50,0,0)
# Vertices: apex=(50,0,0), left=(30,30,0), right=(70,30,0)
p_ti_apex  = p_smid  # shared with outer boundary — this IS the splitting vertex
p_ti_left  = f.cartesian_point((30.0, 30.0, 0.0))
p_ti_right = f.cartesian_point((70.0, 30.0, 0.0))

vti_apex  = vsmid  # reuse the T-vertex
vti_left  = f.vertex_point(p_ti_left)
vti_right = f.vertex_point(p_ti_right)

# Inner loop edges (CW from above = hole):  apex→right, right→left, left→apex
import math
dx_ar = 70.0 - 50.0; dy_ar = 30.0 - 0.0
mag_ar = math.hypot(dx_ar, dy_ar)
e_ti_ar = f.edge_curve(vti_apex, vti_right, f.line(p_smid, f.vector(f.direction((dx_ar/mag_ar, dy_ar/mag_ar, 0.0)), mag_ar)))
e_ti_rl = f.edge_curve(vti_right, vti_left, f.line(p_ti_right, f.vector(f.direction((-1.0, 0.0, 0.0)), 40.0)))
dx_la = 30.0 - 50.0; dy_la = 0.0 - 30.0
mag_la = math.hypot(dx_la, dy_la)
e_ti_la = f.edge_curve(vti_left, vti_apex, f.line(p_ti_left, f.vector(f.direction((dx_la/mag_la, dy_la/mag_la, 0.0)), mag_la)))

inner_tri_loop = f.edge_loop([
    f.oriented_edge(e_ti_ar, True),
    f.oriented_edge(e_ti_rl, True),
    f.oriented_edge(e_ti_la, True),
])
inner_tri_fb = f.face_bound(inner_tri_loop, orientation=False)

ax_bot = f.axis2_placement_3d(p_s0, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
face_bot = f.advanced_face([bot_outer_fob, inner_tri_fb], f.plane(ax_bot))

# ── Top face z=H (simple rectangle) ─────────────────────────────────────────
p001 = f.cartesian_point((0.0, 0.0, H)); p101 = f.cartesian_point((W,   0.0, H))
p111 = f.cartesian_point((W,   W,   H)); p011 = f.cartesian_point((0.0, W,   H))
v001 = f.vertex_point(p001); v101 = f.vertex_point(p101)
v111 = f.vertex_point(p111); v011 = f.vertex_point(p011)

et0 = f.edge_curve(v001, v101, f.line(p001, f.vector(f.direction(( 1.0, 0.0, 0.0)), W)))
et1 = f.edge_curve(v101, v111, f.line(p101, f.vector(f.direction(( 0.0, 1.0, 0.0)), W)))
et2 = f.edge_curve(v111, v011, f.line(p111, f.vector(f.direction((-1.0, 0.0, 0.0)), W)))
et3 = f.edge_curve(v011, v001, f.line(p011, f.vector(f.direction(( 0.0,-1.0, 0.0)), W)))

top_loop = f.edge_loop([
    f.oriented_edge(et0, True), f.oriented_edge(et1, True),
    f.oriented_edge(et2, True), f.oriented_edge(et3, True),
])
ax_top = f.axis2_placement_3d(p001, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face_top = f.advanced_face([f.face_outer_bound(top_loop)], f.plane(ax_top))

# ── Vertical edges connecting bottom and top ─────────────────────────────────
# Use simplified box: 4 corners at bottom corners (s0, s1, e, n) → top corners
p_bot_s1 = p_s1
p_bot_e  = p_e
p_bot_n  = p_n
p_bot_s0 = p_s0

ev0 = f.edge_curve(vs0, v001, f.line(p_s0, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev1 = f.edge_curve(vs1, v101, f.line(p_s1, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev2 = f.edge_curve(ve,  v111, f.line(p_e,  f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev3 = f.edge_curve(vn,  v011, f.line(p_n,  f.vector(f.direction((0.0, 0.0, 1.0)), H)))

# South face y=0 (uses e_sw, e_se split)
frt_loop = f.edge_loop([
    f.oriented_edge(e_sw, True), f.oriented_edge(e_se, True),
    f.oriented_edge(ev1, True), f.oriented_edge(et0, False), f.oriented_edge(ev0, False),
])
ax_frt = f.axis2_placement_3d(p_s0, f.direction((0.0, -1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face_frt = f.advanced_face([f.face_outer_bound(frt_loop)], f.plane(ax_frt))

# East face x=W
ert_loop = f.edge_loop([
    f.oriented_edge(e_e, True), f.oriented_edge(ev2, True),
    f.oriented_edge(et1, False), f.oriented_edge(ev1, False),
])
ax_ert = f.axis2_placement_3d(p_s1, f.direction((1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face_ert = f.advanced_face([f.face_outer_bound(ert_loop)], f.plane(ax_ert))

# North face y=W
nrt_loop = f.edge_loop([
    f.oriented_edge(ev3, True), f.oriented_edge(et2, False),
    f.oriented_edge(ev2, False), f.oriented_edge(e_n, False),
])
ax_nrt = f.axis2_placement_3d(p_n, f.direction((0.0, 1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face_nrt = f.advanced_face([f.face_outer_bound(nrt_loop)], f.plane(ax_nrt))

# West face x=0
wst_loop = f.edge_loop([
    f.oriented_edge(ev0, True), f.oriented_edge(et3, False),
    f.oriented_edge(ev3, False), f.oriented_edge(e_w, False),
])
ax_wst = f.axis2_placement_3d(p_s0, f.direction((-1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face_wst = f.advanced_face([f.face_outer_bound(wst_loop)], f.plane(ax_wst))

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face_bot, face_top, face_frt, face_ert, face_nrt, face_wst])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa079.stp")
