"""Gs048 — OFFSET_CURVE_2D with sign of ref_distance flipping mid composite-curve chain.

Catalog claim: COMPOSITE_CURVE of two POLYLINE segments, each wrapped in
OFFSET_CURVE_2D with ref_distance = +1.0 on the first segment and -1.0 on the
second. The sign flip means the two offset segments do not meet at the junction,
producing a C0 discontinuity (gap) in the offset chain.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - PLANE IS the ADVANCED_FACE.face_geometry.
  - OFFSET_CURVE_2D('off1', #N, 1.0, .T.) and OFFSET_CURVE_2D('off2', #M, -1.0, .T.)
    (opposite-sign offsets of adjacent POLYLINE segments) ARE the curves of two
    COMPOSITE_CURVE_SEGMENTs that share a junction point; opposite signs mean
    segments depart to opposite sides — gap IS wired into face edge topology.
  - Byte assertions: count_entity_def(b'OFFSET_CURVE_2D') == 2,
                     contains(b"OFFSET_CURVE_2D('off1',#20,1.0,.T.)"),
                     contains(b"OFFSET_CURVE_2D('off2',#21,-1.0,.T.)").
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE IS the ADVANCED_FACE.face_geometry;
    two OFFSET_CURVE_2D segments with opposite ref_distance signs chained in a
    COMPOSITE_CURVE — producing a C0 discontinuity — ARE the curve_3d of the
    defect EDGE_CURVE; sign-flip gap IS wired into face topology.
  - shape_null driver: gap at offset-chain junction; strict reject kernels produce
    empty result.

Note on byte assertions: catalog requires the literal strings
"OFFSET_CURVE_2D('off1',#20,1.0,.T.)" and "OFFSET_CURVE_2D('off2',#21,-1.0,.T.)".
The two POLYLINE basis curves must be the 20th and 21st entities respectively.
We front-load the PLANE and prc so that poly1 lands at #20 and poly2 at #21.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs048",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; "
        "OFFSET_CURVE_2D('off1',...,+1.0) and OFFSET_CURVE_2D('off2',...,-1.0) — "
        "opposite-sign offsets of adjacent POLYLINE segments chained in COMPOSITE_CURVE — "
        "sign flip creates C0 gap at junction IS wired into face edge topology; shape(1) (live OCC heals)"
    ),
)

# ── PLANE as face_geometry (emitted first to push POLYLINE entities toward #20/#21) ─
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
ax3   = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs048_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('gs048_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Two POLYLINE basis curves for the OFFSET_CURVE_2D segments ────────────────
# Segment 1: from (0,0) to (5,0) along X
pA = f.cartesian_point((0.0, 0.0, 0.0))
pB = f.cartesian_point((5.0, 0.0, 0.0))
# Segment 2: from (5,0) to (10,0) along X
pC = f.cartesian_point((10.0, 0.0, 0.0))

# Byte assertion: contains(b"OFFSET_CURVE_2D('off1',#20,1.0,.T.)")
# Byte assertion: contains(b"OFFSET_CURVE_2D('off2',#21,-1.0,.T.)")
# poly1 must land at #20 and poly2 at #21.
# Currently at entity #10 after: orig(#1),zdir(#2),xdir(#3),ax3(#4),plane(#5),
# prc(#6),pA(#7),pB(#8),pC(#9). Pad 10 more (#10..#19) so poly1 → #20, poly2 → #21.
for _j in range(10):
    f.cartesian_point((float(_j), 0.0, 0.0))   # padding to reach entity #20 for poly1
poly1 = f._emit_raw(f"POLYLINE('gs048_poly1',(#{pA.eid},#{pB.eid}))")   # entity #20
poly2 = f._emit_raw(f"POLYLINE('gs048_poly2',(#{pB.eid},#{pC.eid}))")   # entity #21

# OFFSET_CURVE_2D(name, basis_curve, distance, self_intersect)
# Byte assertion: count_entity_def(b'OFFSET_CURVE_2D') == 2
off1 = f._emit_raw(f"OFFSET_CURVE_2D('off1',#{poly1.eid},1.0,.T.)")
off2 = f._emit_raw(f"OFFSET_CURVE_2D('off2',#{poly2.eid},-1.0,.T.)")

# ── COMPOSITE_CURVE chaining both offset segments ─────────────────────────────
ccs1 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{off1.eid})")
ccs2 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{off2.eid})")
cc   = f._emit_raw(f"COMPOSITE_CURVE('gs048_cc',(#{ccs1.eid},#{ccs2.eid}),.T.)")

# ── Face boundary: defect edge uses COMPOSITE_CURVE (sign-flip offset chain) ──
p_A3 = f.cartesian_point(( 0.0, 0.0, 0.0))
p_B3 = f.cartesian_point((10.0, 0.0, 0.0))
p_C3 = f.cartesian_point((10.0, 4.0, 0.0))
p_D3 = f.cartesian_point(( 0.0, 4.0, 0.0))

v_A = f.vertex_point(p_A3)
v_B = f.vertex_point(p_B3)
v_C = f.vertex_point(p_C3)
v_D = f.vertex_point(p_D3)

# Defect edge E0: curve_3d IS the COMPOSITE_CURVE of opposite-sign offsets
p2_e0  = f.cartesian_point((0.0, 0.0))
d2_e0  = f.direction((1.0, 0.0))
v2_e0  = f.vector(d2_e0, 10.0)
l2_e0  = f.line(p2_e0, v2_e0)
pcd_e0 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_e0',(#{l2_e0.eid}),#{prc.eid})")
pc_e0  = f._emit_raw(f"PCURVE('pc_e0',#{plane.eid},#{pcd_e0.eid})")
sc_e0  = f._emit_raw(f"SURFACE_CURVE('sc_e0',#{cc.eid},(#{pc_e0.eid}),.PCURVE_S1.)")
e0 = f._emit_raw(f"EDGE_CURVE('ec_e0',#{v_A.eid},#{v_B.eid},#{sc_e0.eid},.T.)")

def mk_edge_line(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e1 = mk_edge_line(v_B, v_C, (10.0,0.0,0.0), (0.0,1.0,0.0), 4.0, (10.0,0.0), (0.0,1.0), 4.0)
e2 = mk_edge_line(v_C, v_D, (10.0,4.0,0.0), (-1.0,0.0,0.0), 10.0, (10.0,4.0), (-1.0,0.0), 10.0)
e3 = mk_edge_line(v_D, v_A, (0.0,4.0,0.0), (0.0,-1.0,0.0), 4.0, (0.0,4.0), (0.0,-1.0), 4.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# PLANE IS the face_geometry; OFFSET_CURVE_2D sign-flip chain IS defect edge 3D curve.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
