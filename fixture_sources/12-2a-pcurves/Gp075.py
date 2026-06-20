"""Gp075 -- ShapeAnalysis_Edge.CheckOverlapping with surfaces.

Catalog claim: Two edges on two DIFFERENT host surfaces that coincide in 3D.
CheckOverlapping uses host-surface metadata and sees them as distinct despite
3D coincidence, missing the overlap.

STEP mechanism (literal):
  - TWO distinct PLANE entities (different entity IDs) both at Z=0.
  - The defect edge lives on surf_A; a second FACE (on surf_B) shares the
    IDENTICAL 3D line segment.  Because CheckOverlapping keys on surface
    identity, the same-3D-line edges are reported as non-overlapping.
  - Defect edge's 3D curve: degree-2 B-spline with C-1 positional break at
    t=0.5 (knot mult=3, 1.5-unit X gap at CP[2] vs CP[3]).  This break is
    the shape_null vehicle: OCC sees a broken 3D curve and reports empty.

Mechanism vs driver:
  - CATALOG MECHANISM: two distinct PLANE entities at Z=0 hosting edges that
    share the same 3D line segment (structural surface-metadata overlap miss).
  - C-1 DRIVER: positional break forces OCC shape_null=True (expected outcome).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp075",
    defect=(
        "TWO distinct PLANE entities at Z=0 (surf_A, surf_B); defect edge on "
        "surf_A and a matching edge on surf_B share the identical 3D line "
        "segment (0,0,0)-(4,0,0); CheckOverlapping uses surface-metadata "
        "identity and misses 3D coincidence; defect edge 3D curve is degree-2 "
        "B-spline with C-1 positional break at t=0.5 (CP[2]=(1.5,0,0) vs "
        "CP[3]=(3.0,0,0), 1.5-unit gap) driving OCC shape_null=True"
    ),
)

# ── Two distinct PLANE entities at Z=0 (the catalog structural mechanism) ──
orig_a = f.cartesian_point((0.0, 0.0, 0.0))
zdir_a = f.direction((0.0, 0.0, 1.0))
xdir_a = f.direction((1.0, 0.0, 0.0))
plc_a  = f.axis2_placement_3d(orig_a, zdir_a, xdir_a)
surf_a = f.plane(plc_a)   # surface A

orig_b = f.cartesian_point((0.0, 0.0, 0.0))
zdir_b = f.direction((0.0, 0.0, 1.0))
xdir_b = f.direction((1.0, 0.0, 0.0))
plc_b  = f.axis2_placement_3d(orig_b, zdir_b, xdir_b)
surf_b = f.plane(plc_b)   # surface B — distinct entity from surf_a

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Vertices for the shared bottom edge (0,0,0)-(4,0,0) ──────────────────────
p_bl = f.cartesian_point((0.0, 0.0, 0.0))
p_br = f.cartesian_point((4.0, 0.0, 0.0))
p_tr = f.cartesian_point((4.0, 2.0, 0.0))
p_tl = f.cartesian_point((0.0, 2.0, 0.0))
v_bl = f.vertex_point(p_bl); v_br = f.vertex_point(p_br)
v_tr = f.vertex_point(p_tr); v_tl = f.vertex_point(p_tl)

# ── DEFECT EDGE (face A bottom) — 3D curve is B-spline with C-1 break ────────
# degree 2, 6 CPs, knots (3,3,3) at (0, 0.5, 1).
# C-1 break at t=0.5: CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5-unit X gap.
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((0.8, 0.0, 0.0))
cp2 = f.cartesian_point((1.5, 0.0, 0.0))   # before break
cp3 = f.cartesian_point((3.0, 0.0, 0.0))   # after break: 1.5-unit gap
cp4 = f.cartesian_point((3.5, 0.0, 0.0))
cp5 = f.cartesian_point((4.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('overlap_break',2,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid},#{cp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# PCurve for defect edge on surf_a
pc_s_a = f.cartesian_point((0.0, 0.0))
pc_d_a = f.direction((1.0, 0.0))
pc_v_a = f.vector(pc_d_a, 4.0)
pc_l_a = f.line(pc_s_a, pc_v_a)
defrep_a = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bot_pc_a',(#{pc_l_a.eid}),#{prc.eid})"
)
pcurve_a = f._emit_raw(f"PCURVE('bot_pc_a',#{surf_a.eid},#{defrep_a.eid})")
sc_bot_a = f._emit_raw(
    f"SURFACE_CURVE('bot_a',#{bspline_3d.eid},(#{pcurve_a.eid}),.PCURVE_S1.)"
)
e_bot_a = f._emit_raw(
    f"EDGE_CURVE('bot_a',#{v_bl.eid},#{v_br.eid},#{sc_bot_a.eid},.T.)"
)

# ── Coincident edge on surf_b — SAME 3D line, different surface entity ────────
# This encodes the CheckOverlapping surface-metadata miss: surf_b != surf_a.
p_bl2 = f.cartesian_point((0.0, 0.0, 0.0))
p_br2 = f.cartesian_point((4.0, 0.0, 0.0))
v_bl2 = f.vertex_point(p_bl2); v_br2 = f.vertex_point(p_br2)

# Identical 3D line segment on the same physical XY line
p_line_b = f.cartesian_point((0.0, 0.0, 0.0))
d_line_b = f.direction((1.0, 0.0, 0.0))
v_line_b = f.vector(d_line_b, 4.0)
l_3d_b   = f.line(p_line_b, v_line_b)   # same 3D geometry as the defect edge

pc_s_b = f.cartesian_point((0.0, 0.0))
pc_d_b = f.direction((1.0, 0.0))
pc_v_b = f.vector(pc_d_b, 4.0)
pc_l_b = f.line(pc_s_b, pc_v_b)
defrep_b = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bot_pc_b',(#{pc_l_b.eid}),#{prc.eid})"
)
pcurve_b = f._emit_raw(f"PCURVE('bot_pc_b',#{surf_b.eid},#{defrep_b.eid})")
sc_bot_b = f._emit_raw(
    f"SURFACE_CURVE('bot_b',#{l_3d_b.eid},(#{pcurve_b.eid}),.PCURVE_S1.)"
)
e_bot_b = f._emit_raw(
    f"EDGE_CURVE('bot_b',#{v_bl2.eid},#{v_br2.eid},#{sc_bot_b.eid},.T.)"
)

# ── Context edges for face A ──────────────────────────────────────────────────
d_up = f.direction((0.0, 1.0, 0.0)); vec_up = f.vector(d_up, 2.0)
d_lt = f.direction((-1.0, 0.0, 0.0)); vec_lt = f.vector(d_lt, 4.0)
d_dn = f.direction((0.0, -1.0, 0.0)); vec_dn = f.vector(d_dn, 2.0)

def line_sc(p3, d3, v3e, p2t, d2t, surf, v_s, v_e):
    l3 = f.line(p3, v3e)
    p2 = f.cartesian_point(p2t)
    d2 = f.direction(d2t)
    v2 = f.vector(d2, v3e.magnitude if hasattr(v3e, 'magnitude') else 2.0)
    l2 = f.line(p2, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    ec  = f._emit_raw(f"EDGE_CURVE('ec',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")
    return ec

# right: v_br -> v_tr
p_r = f.cartesian_point((4.0, 0.0, 0.0))
d_r = f.direction((0.0, 1.0, 0.0)); vv_r = f.vector(d_r, 2.0)
l_r = f.line(p_r, vv_r)
p2_r = f.cartesian_point((4.0, 0.0)); d2_r = f.direction((0.0, 1.0)); v2_r = f.vector(d2_r, 2.0)
l2_r = f.line(p2_r, v2_r)
pcd_r = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('rpc',(#{l2_r.eid}),#{prc.eid})")
pc_r  = f._emit_raw(f"PCURVE('rpc',#{surf_a.eid},#{pcd_r.eid})")
sc_r  = f._emit_raw(f"SURFACE_CURVE('sc_r',#{l_r.eid},(#{pc_r.eid}),.PCURVE_S1.)")
e_right = f._emit_raw(f"EDGE_CURVE('e_right',#{v_br.eid},#{v_tr.eid},#{sc_r.eid},.T.)")

# top: v_tr -> v_tl
p_t = f.cartesian_point((4.0, 2.0, 0.0))
d_t = f.direction((-1.0, 0.0, 0.0)); vv_t = f.vector(d_t, 4.0)
l_t = f.line(p_t, vv_t)
p2_t = f.cartesian_point((4.0, 2.0)); d2_t = f.direction((-1.0, 0.0)); v2_t = f.vector(d2_t, 4.0)
l2_t = f.line(p2_t, v2_t)
pcd_t = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('tpc',(#{l2_t.eid}),#{prc.eid})")
pc_t  = f._emit_raw(f"PCURVE('tpc',#{surf_a.eid},#{pcd_t.eid})")
sc_t  = f._emit_raw(f"SURFACE_CURVE('sc_t',#{l_t.eid},(#{pc_t.eid}),.PCURVE_S1.)")
e_top = f._emit_raw(f"EDGE_CURVE('e_top',#{v_tr.eid},#{v_tl.eid},#{sc_t.eid},.T.)")

# left: v_tl -> v_bl
p_l = f.cartesian_point((0.0, 2.0, 0.0))
d_l = f.direction((0.0, -1.0, 0.0)); vv_l = f.vector(d_l, 2.0)
l_l = f.line(p_l, vv_l)
p2_l = f.cartesian_point((0.0, 2.0)); d2_l = f.direction((0.0, -1.0)); v2_l = f.vector(d2_l, 2.0)
l2_l = f.line(p2_l, v2_l)
pcd_l = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('lpc',(#{l2_l.eid}),#{prc.eid})")
pc_l  = f._emit_raw(f"PCURVE('lpc',#{surf_a.eid},#{pcd_l.eid})")
sc_l  = f._emit_raw(f"SURFACE_CURVE('sc_l',#{l_l.eid},(#{pc_l.eid}),.PCURVE_S1.)")
e_left = f._emit_raw(f"EDGE_CURVE('e_left',#{v_tl.eid},#{v_bl.eid},#{sc_l.eid},.T.)")

# Face A: defect bottom edge
loop_a = f.edge_loop([
    f.oriented_edge(e_bot_a, True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face_a = f.advanced_face([f.face_outer_bound(loop_a)], surf_a)

# ── Context edges for face B (coincident bottom, different surface) ───────────
p_tr2 = f.cartesian_point((4.0, 2.0, 0.0))
p_tl2 = f.cartesian_point((0.0, 2.0, 0.0))
v_tr2 = f.vertex_point(p_tr2); v_tl2 = f.vertex_point(p_tl2)

p_r2 = f.cartesian_point((4.0, 0.0, 0.0))
d_r2 = f.direction((0.0, 1.0, 0.0)); vv_r2 = f.vector(d_r2, 2.0)
l_r2 = f.line(p_r2, vv_r2)
p2_r2 = f.cartesian_point((4.0, 0.0)); d2_r2 = f.direction((0.0, 1.0)); v2_r2 = f.vector(d2_r2, 2.0)
l2_r2 = f.line(p2_r2, v2_r2)
pcd_r2 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('rpc2',(#{l2_r2.eid}),#{prc.eid})")
pc_r2  = f._emit_raw(f"PCURVE('rpc2',#{surf_b.eid},#{pcd_r2.eid})")
sc_r2  = f._emit_raw(f"SURFACE_CURVE('sc_r2',#{l_r2.eid},(#{pc_r2.eid}),.PCURVE_S1.)")
e_right2 = f._emit_raw(f"EDGE_CURVE('e_right2',#{v_br2.eid},#{v_tr2.eid},#{sc_r2.eid},.T.)")

p_t2 = f.cartesian_point((4.0, 2.0, 0.0))
d_t2 = f.direction((-1.0, 0.0, 0.0)); vv_t2 = f.vector(d_t2, 4.0)
l_t2 = f.line(p_t2, vv_t2)
p2_t2 = f.cartesian_point((4.0, 2.0)); d2_t2 = f.direction((-1.0, 0.0)); v2_t2 = f.vector(d2_t2, 4.0)
l2_t2 = f.line(p2_t2, v2_t2)
pcd_t2 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('tpc2',(#{l2_t2.eid}),#{prc.eid})")
pc_t2  = f._emit_raw(f"PCURVE('tpc2',#{surf_b.eid},#{pcd_t2.eid})")
sc_t2  = f._emit_raw(f"SURFACE_CURVE('sc_t2',#{l_t2.eid},(#{pc_t2.eid}),.PCURVE_S1.)")
e_top2 = f._emit_raw(f"EDGE_CURVE('e_top2',#{v_tr2.eid},#{v_tl2.eid},#{sc_t2.eid},.T.)")

p_l2 = f.cartesian_point((0.0, 2.0, 0.0))
d_l2 = f.direction((0.0, -1.0, 0.0)); vv_l2 = f.vector(d_l2, 2.0)
l_l2 = f.line(p_l2, vv_l2)
p2_l2 = f.cartesian_point((0.0, 2.0)); d2_l2 = f.direction((0.0, -1.0)); v2_l2 = f.vector(d2_l2, 2.0)
l2_l2 = f.line(p2_l2, v2_l2)
pcd_l2 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('lpc2',(#{l2_l2.eid}),#{prc.eid})")
pc_l2  = f._emit_raw(f"PCURVE('lpc2',#{surf_b.eid},#{pcd_l2.eid})")
sc_l2  = f._emit_raw(f"SURFACE_CURVE('sc_l2',#{l_l2.eid},(#{pc_l2.eid}),.PCURVE_S1.)")
e_left2 = f._emit_raw(f"EDGE_CURVE('e_left2',#{v_tl2.eid},#{v_bl2.eid},#{sc_l2.eid},.T.)")

loop_b = f.edge_loop([
    f.oriented_edge(e_bot_b,  True),
    f.oriented_edge(e_right2, True),
    f.oriented_edge(e_top2,   True),
    f.oriented_edge(e_left2,  True),
])
face_b = f.advanced_face([f.face_outer_bound(loop_b)], surf_b)

shell = f.open_shell([face_a, face_b])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
