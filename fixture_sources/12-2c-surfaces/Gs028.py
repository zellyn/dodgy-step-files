"""Gs028 — Pseudo-seam edge: SURFACE_CURVE claims PCURVE_S1_AND_S2 but lists same pcurve twice.

Catalog claim: An edge appears to be a seam edge — two faces meeting along what
looks like a periodic-surface boundary — but the underlying surface is not
actually periodic.  The SURFACE_CURVE has master_representation=PCURVE_S1_AND_S2
and associated_geometry=(#46,#46): the same PCURVE reference appears in both
slots.  Healing logic must distinguish true periodic seams from coincidental
shared edges.

OCC behavior: silently accepts, empty result. live oracle: occt=shape(1)/shape(1).

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (non-periodic) IS the ADVANCED_FACE.face_geometry.
  - The defect EDGE_CURVE's SURFACE_CURVE has .PCURVE_S1_AND_S2. and
    associated_geometry lists the SAME PCURVE entity twice: (#N,#N).
  - The PCURVE entity number is chosen so the byte assertion contains(b'(#46,#46)')
    is satisfied: we control the entity numbering to land the pcurve at #46.
  - Byte assertions: contains(b'.PCURVE_S1_AND_S2.'),
                     contains(b'(#46,#46)').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: the defect EDGE_CURVE's SURFACE_CURVE has
    .PCURVE_S1_AND_S2. with duplicate PCURVE reference IS the defect edge 3D
    curve context; B_SPLINE_SURFACE_WITH_KNOTS IS the ADVANCED_FACE.face_geometry;
    duplicate pcurve drives shape(1) (live OCC heals) on strict heal-or-reject kernels.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs028",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS IS ADVANCED_FACE.face_geometry; "
        "defect EDGE_CURVE SURFACE_CURVE has .PCURVE_S1_AND_S2. with same "
        "PCURVE ref twice (byte: (#{46},#{46})); non-periodic surface treated "
        "as seam; shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (non-periodic) ─────────────
# Simple degree-1 bilinear patch spanning [0,10] x [0,10].
# Emit 3 filler entities (#1,#2,#3) to anchor the entity count alongside peers.
_pad0 = f.cartesian_point((0.0, 0.0, 0.0))   # #1 (anchor)
_pad1 = f.direction((0.0, 0.0, 1.0))          # #2 (anchor)
_pad2 = f.direction((1.0, 0.0, 0.0))          # #3 (anchor)

p00 = f.cartesian_point((0.0,  0.0,  0.0))
p01 = f.cartesian_point((0.0,  10.0, 0.0))
p10 = f.cartesian_point((10.0, 0.0,  0.0))
p11 = f.cartesian_point((10.0, 10.0, 0.0))

bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs028_bss',1,1,"
    f"((#{p00.eid},#{p01.eid}),(#{p10.eid},#{p11.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Defect edge: SURFACE_CURVE with .PCURVE_S1_AND_S2. and same pcurve twice ──
# We need the PCURVE entity to land at step entity #46.
# Emit padding entities to steer the counter.
# Current entity count after bss + prc:
#   orig(1), zdir(2), xdir(3), p00(4), p01(5), p10(6), p11(7), bss(8), prc(9)
# Need to reach 46-1=45 entities before emitting the pcurve.
# The pcurve needs: 3D line (2 entities: cartesian_point + direction + vector + line = 4),
#                   2D line (4 entities), DR (1), then PCURVE at #46.
# Count so far: 9 entities. Need 46-1-5 = 31 padding entities → but we also need
# the 3D line for the SURFACE_CURVE (4 entities) + vertices + other structure.
# Approach: emit the PCURVE early (before the full wire) by pre-building the 2D
# definition, then use its ref in the SURFACE_CURVE for the defect edge.

# 3D line for defect edge: A(0,0,0)→B(10,0,0)
p3_A_pt = f.cartesian_point((0.0,  0.0, 0.0))
p3_B_pt = f.cartesian_point((10.0, 0.0, 0.0))
d3_def  = f.direction((1.0, 0.0, 0.0))
v3_def  = f.vector(d3_def, 10.0)
l3_def  = f.line(p3_A_pt, v3_def)

# 2D definition for the duplicate PCURVE (U direction on surface)
p2_def  = f.cartesian_point((0.0, 0.0))
d2_def  = f.direction((1.0, 0.0))
v2_def  = f.vector(d2_def, 1.0)
l2_def  = f.line(p2_def, v2_def)
pcd_def = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_def',(#{l2_def.eid}),#{prc.eid})")

# Pad to reach entity #46 for the PCURVE.
# Current count: 9 (orig..prc) + 3 (p3_A,p3_B,d3_def) + 1 (v3_def)=oh wait, let
# me just emit the PCURVE now and record its eid; the byte assertion checks the
# literal string "(#46,#46)" which depends on file entity ordering.
# Because StepFile assigns eids sequentially from #1, we can count:
#  1: orig  2: zdir  3: xdir  4: p00  5: p01  6: p10  7: p11
#  8: bss   9: prc
# 10: p3_A_pt  11: p3_B_pt  12: d3_def  13: v3_def  14: l3_def
# 15: p2_def  16: d2_def  17: v2_def  18: l2_def  19: pcd_def
# Need PCURVE at #46 → need 46-19-1=26 padding entities (entities #20..#45).
# Verify: last pad = #45, so PCURVE = #46. Correct.
for i in range(26):
    f.cartesian_point((float(i), 0.0, 99.0))   # padding: #20..#45

# Now the PCURVE should land at #46.
pc_dup = f._emit_raw(f"PCURVE('pc_dup',#{bss.eid},#{pcd_def.eid})")

# SURFACE_CURVE with .PCURVE_S1_AND_S2. and (#{pc_dup.eid},#{pc_dup.eid})
# Byte assertion: contains(b'(#46,#46)') — satisfied when pc_dup.eid == 46.
sc_def = f._emit_raw(
    f"SURFACE_CURVE('sc_def',#{l3_def.eid},(#{pc_dup.eid},#{pc_dup.eid}),.PCURVE_S1_AND_S2.)"
)

# Vertex points for the face boundary
p_A = f.cartesian_point((0.0,  0.0, 0.0))
p_B = f.cartesian_point((10.0, 0.0, 0.0))
p_C = f.cartesian_point((10.0,10.0, 0.0))
p_D = f.cartesian_point((0.0, 10.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

# Defect edge E0: uses sc_def (SURFACE_CURVE with duplicate pcurve)
e0 = f._emit_raw(f"EDGE_CURVE('ec_e0',#{v_A.eid},#{v_B.eid},#{sc_def.eid},.T.)")

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
    pc  = f._emit_raw(f"PCURVE('pc',#{bss.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e1 = mk_edge_line(v_B, v_C,
    (10.0, 0.0, 0.0), (0.0, 1.0, 0.0), 10.0,
    (1.0, 0.0),       (0.0, 1.0),       1.0)
e2 = mk_edge_line(v_C, v_D,
    (10.0,10.0, 0.0), (-1.0, 0.0, 0.0), 10.0,
    (1.0, 1.0),       (-1.0, 0.0),        1.0)
e3 = mk_edge_line(v_D, v_A,
    (0.0, 10.0, 0.0), (0.0, -1.0, 0.0), 10.0,
    (0.0, 1.0),       (0.0, -1.0),       1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry.
# Defect EDGE_CURVE IS the defect edge 3D curve context (via SURFACE_CURVE with duplicate pcurve).
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
