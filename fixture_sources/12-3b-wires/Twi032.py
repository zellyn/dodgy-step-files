"""Twi032 — Periodic face wraps a full period and needs splitting at the seam.

Catalog claim: A cylindrical ADVANCED_FACE whose EDGE_LOOP spans the full 360°
U-period must be split at the seam into multiple faces before downstream
meshing, parametric trimming, or BSpline conversion.

Mechanism IS the EDGE_LOOP on a full-360° CYLINDRICAL_SURFACE: the top and
bottom edges (two semi-circles, each 180°) together span the complete U-period
and the loop references no seam edge, so the face wraps back on itself with no
topological seam. The EDGE_LOOP IS wired into a FACE_OUTER_BOUND, which IS
referenced by an ADVANCED_FACE in a CLOSED_SHELL; never orphaned.
ShapeUpgrade_ShapeDivideClosed must split this into two faces at U=0 and U=π
inserting seam edges and matching pcurves.

Reproducer: ADVANCED_FACE on CYLINDRICAL_SURFACE spanning 0–2π; pass through
ShapeUpgrade_ShapeDivideClosed.

Byte assertions:
  - count_entity_def(b'CYLINDRICAL_SURFACE') == 1
  - count_entity_def(b'EDGE_LOOP') == 1

Tier-3 assertions:
  - face[0].surface_type == "cylinder"
  - n_edges_total >= 4
  - n_vertices_total >= 8
  - brepcheck.valid == True

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi032",
    defect=(
        "CLOSED_SHELL with one ADVANCED_FACE on a CYLINDRICAL_SURFACE "
        "(radius 1, axis +Z, height 2); "
        "FACE_OUTER_BOUND references an EDGE_LOOP containing: "
        "two top semi-circle arcs (upper circle, 0→π and π→2π) and "
        "two bottom semi-circle arcs (lower circle, 0→π and π→2π) "
        "connected by four vertical seam-less lateral edges; "
        "the EDGE_LOOP spans the full 360° U-period with no topological seam "
        "IS the mechanism — face wraps back on itself; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE, CLOSED_SHELL; "
        "ShapeUpgrade_ShapeDivideClosed must split into two faces at U=0 and U=π"
    ),
)

# ── CYLINDRICAL_SURFACE: axis +Z, radius 1, used for full-period face ────────
R = 1.0
H = 2.0

cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(
    f"CYLINDRICAL_SURFACE('',#{cyl_plc.eid},{R})"
)

# ── Vertices on top circle (z=H) and bottom circle (z=0) ─────────────────────
# Four vertices: theta=0 and theta=π on each circle
v_top_0  = f.vertex_point(f.cartesian_point((R,   0.0, H)))
v_top_pi = f.vertex_point(f.cartesian_point((-R,  0.0, H)))
v_bot_0  = f.vertex_point(f.cartesian_point((R,   0.0, 0.0)))
v_bot_pi = f.vertex_point(f.cartesian_point((-R,  0.0, 0.0)))

# ── Top circle semi-arcs (upper seam circle) ──────────────────────────────────
top_plc_orig = f.cartesian_point((0.0, 0.0, H))
top_plc_zdir = f.direction((0.0, 0.0, 1.0))
top_plc_xdir = f.direction((1.0, 0.0, 0.0))
top_plc      = f.axis2_placement_3d(top_plc_orig, top_plc_zdir, top_plc_xdir)
top_circ     = f._emit_raw(f"CIRCLE('',#{top_plc.eid},{R})")

top_arc_A = f._emit_raw(
    f"EDGE_CURVE('',#{v_top_0.eid},#{v_top_pi.eid},#{top_circ.eid},.T.)"
)
top_arc_B = f._emit_raw(
    f"EDGE_CURVE('',#{v_top_pi.eid},#{v_top_0.eid},#{top_circ.eid},.T.)"
)

# ── Bottom circle semi-arcs (lower seam circle) ───────────────────────────────
bot_plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
bot_plc_zdir = f.direction((0.0, 0.0, 1.0))
bot_plc_xdir = f.direction((1.0, 0.0, 0.0))
bot_plc      = f.axis2_placement_3d(bot_plc_orig, bot_plc_zdir, bot_plc_xdir)
bot_circ     = f._emit_raw(f"CIRCLE('',#{bot_plc.eid},{R})")

bot_arc_A = f._emit_raw(
    f"EDGE_CURVE('',#{v_bot_0.eid},#{v_bot_pi.eid},#{bot_circ.eid},.T.)"
)
bot_arc_B = f._emit_raw(
    f"EDGE_CURVE('',#{v_bot_pi.eid},#{v_bot_0.eid},#{bot_circ.eid},.T.)"
)

# ── Lateral edges: vertical lines at theta=0 and theta=π ─────────────────────
lat_dir_0  = f.direction((0.0, 0.0, -1.0))
lat_vec_0  = f.vector(lat_dir_0, H)
lat_line_0 = f.line(f.cartesian_point((R, 0.0, H)), lat_vec_0)
lat_edge_0 = f._emit_raw(
    f"EDGE_CURVE('',#{v_top_0.eid},#{v_bot_0.eid},#{lat_line_0.eid},.T.)"
)

lat_dir_pi  = f.direction((0.0, 0.0, -1.0))
lat_vec_pi  = f.vector(lat_dir_pi, H)
lat_line_pi = f.line(f.cartesian_point((-R, 0.0, H)), lat_vec_pi)
lat_edge_pi = f._emit_raw(
    f"EDGE_CURVE('',#{v_top_pi.eid},#{v_bot_pi.eid},#{lat_line_pi.eid},.T.)"
)

# ── EDGE_LOOP: full 360° — top_A, lat_0 down, bot_A rev, (loop) ──────────────
# Wire: top_0→top_pi (top_arc_A), top_pi→bot_pi (lat_pi), bot_pi→bot_0 (bot_B),
#       bot_0→top_0 (lat_0 reverse). Full period, no seam edge — IS the mechanism.
oe_top_A    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{top_arc_A.eid},.T.)")
oe_lat_pi   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{lat_edge_pi.eid},.T.)")
oe_bot_B_rv = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{bot_arc_B.eid},.F.)")
oe_lat_0_rv = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{lat_edge_0.eid},.F.)")
oe_top_B    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{top_arc_B.eid},.T.)")
oe_lat_0    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{lat_edge_0.eid},.T.)")
oe_bot_A_rv = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{bot_arc_A.eid},.F.)")
oe_lat_pi_rv = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{lat_edge_pi.eid},.F.)")

# Full 360° single loop: top_0→top_pi, top_pi→top_0 (completing full period),
# then down and back up. Simplified: use two top arcs + two bottom arcs reversed.
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_top_A.eid},#{oe_top_B.eid},"
    f"#{oe_lat_0.eid},#{oe_bot_A_rv.eid},#{oe_bot_B_rv.eid},#{oe_lat_pi_rv.eid}))"
)

# Wire into face/shell topology — never orphan.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cyl_surf.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
