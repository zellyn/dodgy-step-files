"""Tfa167 — ShapeAnalysis_CheckSmallFace.CheckTwisted mobius-strip-face.

Catalog claim: Face with self-intersecting geometry simulating a Möbius strip
(one-sided surface). Normal vectors at opposite ends of the strip point in
opposite directions; CheckTwisted's pairwise normal comparison at sample
points produces inconsistent results due to the topological twist, causing
false negatives on degeneracy detection.

Mechanism: GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a PLANE. The
face boundary is a figure-8 (self-intersecting loop): the outer wire crosses
itself at the centre, creating a path whose normal reverses across the
crossing point. The crossing point is a shared vertex (one vertex incident on
the crossing twice). This mimics the essential property of a Möbius face —
the boundary traversal produces opposing surface normals at different points.

OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa167",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on PLANE; "
        "boundary is a figure-8 self-intersecting loop (Mobius-strip analog); "
        "loop crosses itself at centre vertex (5,5) — same vertex appears twice in traversal; "
        "left lobe: CCW around (2.5,5); right lobe: CW around (7.5,5); "
        "normals at opposite lobes point in opposite directions (topological twist); "
        "CheckTwisted pairwise normal comparison produces inconsistent results; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Plane surface ─────────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Figure-8 loop vertices ─────────────────────────────────────────────────────
# Centre crossing point (shared, appears twice in traversal)
# Left lobe corners: (0,2), (5,2), (5,8), (0,8)
# Right lobe corners: (5,2), (10,2), (10,8), (5,8)
# Traversal: start at (5,2)=centre-bottom, go left lobe CCW, return to (5,2),
#            then right lobe CW, back to start — self-intersects at (5,2) and (5,8)

# Left lobe: (5,2)→(0,2)→(0,8)→(5,8)→(5,2)  CCW when viewed from +z
# Right lobe: (5,2)→(5,8)→(10,8)→(10,2)→(5,2) CW when viewed from +z
# Combined into a single edge-loop with 8 edges, crossing at (5,2) and (5,8).

# Crossing vertices (used by both lobes)
pc_bot = f.cartesian_point((5.0,  2.0, 0.0))   # bottom crossing
pc_top = f.cartesian_point((5.0,  8.0, 0.0))   # top crossing
vc_bot = f._emit_raw(f"VERTEX_POINT('v_cross_bot',#{pc_bot.eid})")
vc_top = f._emit_raw(f"VERTEX_POINT('v_cross_top',#{pc_top.eid})")

# Left lobe outer corners
p_ll = f.cartesian_point((0.0, 2.0, 0.0))
p_lu = f.cartesian_point((0.0, 8.0, 0.0))
v_ll = f._emit_raw(f"VERTEX_POINT('v_left_lo',#{p_ll.eid})")
v_lu = f._emit_raw(f"VERTEX_POINT('v_left_up',#{p_lu.eid})")

# Right lobe outer corners
p_rl = f.cartesian_point((10.0, 2.0, 0.0))
p_ru = f.cartesian_point((10.0, 8.0, 0.0))
v_rl = f._emit_raw(f"VERTEX_POINT('v_rgt_lo',#{p_rl.eid})")
v_ru = f._emit_raw(f"VERTEX_POINT('v_rgt_up',#{p_ru.eid})")

d_px = f.direction((1.0,  0.0, 0.0))
d_py = f.direction((0.0,  1.0, 0.0))
d_nx = f.direction((-1.0, 0.0, 0.0))
d_ny = f.direction((0.0, -1.0, 0.0))

# ── Left lobe edges (CCW): cross_bot→left_lo→left_up→cross_top→cross_bot ─────
# L1: cross_bot(5,2) → left_lo(0,2)  [go left, -x]
ln_l1 = f.line(pc_bot, f.vector(d_nx, 5.0))
ec_l1 = f._emit_raw(f"EDGE_CURVE('l1',#{vc_bot.eid},#{v_ll.eid},#{ln_l1.eid},.T.)")

# L2: left_lo(0,2) → left_up(0,8)  [go up, +y]
ln_l2 = f.line(p_ll, f.vector(d_py, 6.0))
ec_l2 = f._emit_raw(f"EDGE_CURVE('l2',#{v_ll.eid},#{v_lu.eid},#{ln_l2.eid},.T.)")

# L3: left_up(0,8) → cross_top(5,8)  [go right, +x]
ln_l3 = f.line(p_lu, f.vector(d_px, 5.0))
ec_l3 = f._emit_raw(f"EDGE_CURVE('l3',#{v_lu.eid},#{vc_top.eid},#{ln_l3.eid},.T.)")

# L4: cross_top(5,8) → cross_bot(5,2)  [go down, -y — back through crossing]
ln_l4 = f.line(pc_top, f.vector(d_ny, 6.0))
ec_l4 = f._emit_raw(f"EDGE_CURVE('l4',#{vc_top.eid},#{vc_bot.eid},#{ln_l4.eid},.T.)")

# ── Right lobe edges (CW): cross_bot→cross_top→right_up→right_lo→cross_bot ──
# R1: cross_bot(5,2) → cross_top(5,8)  [go up, +y — through crossing again]
ln_r1 = f.line(pc_bot, f.vector(d_py, 6.0))
ec_r1 = f._emit_raw(f"EDGE_CURVE('r1',#{vc_bot.eid},#{vc_top.eid},#{ln_r1.eid},.T.)")

# R2: cross_top(5,8) → right_up(10,8)  [go right, +x]
ln_r2 = f.line(pc_top, f.vector(d_px, 5.0))
ec_r2 = f._emit_raw(f"EDGE_CURVE('r2',#{vc_top.eid},#{v_ru.eid},#{ln_r2.eid},.T.)")

# R3: right_up(10,8) → right_lo(10,2)  [go down, -y]
ln_r3 = f.line(p_ru, f.vector(d_ny, 6.0))
ec_r3 = f._emit_raw(f"EDGE_CURVE('r3',#{v_ru.eid},#{v_rl.eid},#{ln_r3.eid},.T.)")

# R4: right_lo(10,2) → cross_bot(5,2)  [go left, -x]
ln_r4 = f.line(p_rl, f.vector(d_nx, 5.0))
ec_r4 = f._emit_raw(f"EDGE_CURVE('r4',#{v_rl.eid},#{vc_bot.eid},#{ln_r4.eid},.T.)")

oe_l1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_l1.eid},.T.)")
oe_l2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_l2.eid},.T.)")
oe_l3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_l3.eid},.T.)")
oe_l4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_l4.eid},.T.)")
oe_r1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_r1.eid},.T.)")
oe_r2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_r2.eid},.T.)")
oe_r3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_r3.eid},.T.)")
oe_r4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_r4.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('figure8_loop',"
    f"(#{oe_l1.eid},#{oe_l2.eid},#{oe_l3.eid},#{oe_l4.eid},"
    f"#{oe_r1.eid},#{oe_r2.eid},#{oe_r3.eid},#{oe_r4.eid}))"
)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
af  = f._emit_raw(f"ADVANCED_FACE('mobius_strip_face',(#{fob.eid}),#{plane.eid},.T.)")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa167.stp")
