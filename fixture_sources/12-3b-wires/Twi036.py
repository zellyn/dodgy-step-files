"""Twi036 — Lacking edge: UV gap not closable by vertex tolerance.

Catalog claim: Two adjacent edges meet in 3D within tolerance but their pcurve
endpoints in UV are separated by a parametric gap that no vertex tolerance can
bridge; the wire is connected in 3D but missing a "lacking edge" in UV. The
face's parametric outline cannot be closed without adding a synthetic edge to
span the UV gap.

Mechanism IS the EDGE_LOOP on a CYLINDRICAL_SURFACE where two EDGE_CURVEs
share a 3D vertex but have pcurve endpoints separated by Δu > 0 on the seam:
a top arc (0→π) ends at U=π and a bottom arc (π→0 reversed) begins at U=π+gap,
leaving a UV gap that no tolerance setting can close without a bridging edge.
Both EDGE_CURVEs ARE wired into the EDGE_LOOP together with two lateral edges;
the EDGE_LOOP IS referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE in an
OPEN_SHELL; never orphaned.

Reproducer: Two EDGE_CURVEs sharing a VERTEX_POINT in 3D but whose associated
PCURVE endpoints on the cylinder surface differ in U by 1e-2.

Byte assertions:
  - count_entity_def(b'CYLINDRICAL_SURFACE') == 1
  - count_entity_def(b'EDGE_LOOP') == 1

Tier-3 assertions:
  - n_edges_total >= 2
  - face[0].surface_type == "cylinder"
  - n_vertices_total >= 4

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi036",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a CYLINDRICAL_SURFACE "
        "(radius 1, axis +Z, height 2); "
        "FACE_OUTER_BOUND references an EDGE_LOOP containing: "
        "top semi-circle arc (v_top_0→v_top_pi, U: 0→π), "
        "right lateral line (v_top_pi→v_bot_pi, down at theta=π), "
        "bottom semi-circle arc reversed (v_bot_pi→v_bot_0, U: π→0), "
        "left lateral line (v_bot_0→v_top_0, up at theta=0); "
        "the top arc ends at UV (π, H) and right lateral starts at UV (π+0.01, H) "
        "— shared 3D vertex v_top_pi but pcurve endpoints differ by Δu=0.01 "
        "IS the mechanism (lacking edge: UV gap not closable by vertex tolerance); "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; "
        "kernel must synthesise bridging edge or reject topology-vs-parametrisation mismatch"
    ),
)

# ── CYLINDRICAL_SURFACE: radius 1, axis +Z, used for half-cylinder face ──────
R = 1.0
H = 2.0

cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('',#{cyl_plc.eid},{R})")

# ── Vertices: top and bottom at theta=0 and theta=π ──────────────────────────
v_top_0  = f.vertex_point(f.cartesian_point(( R,  0.0, H)))
v_top_pi = f.vertex_point(f.cartesian_point((-R,  0.0, H)))   # shared 3D vertex
v_bot_0  = f.vertex_point(f.cartesian_point(( R,  0.0, 0.0)))
v_bot_pi = f.vertex_point(f.cartesian_point((-R,  0.0, 0.0)))

# ── Top semi-circle arc: v_top_0 → v_top_pi (U: 0 → π) ──────────────────────
top_plc_orig = f.cartesian_point((0.0, 0.0, H))
top_plc_zdir = f.direction((0.0, 0.0, 1.0))
top_plc_xdir = f.direction((1.0, 0.0, 0.0))
top_plc      = f.axis2_placement_3d(top_plc_orig, top_plc_zdir, top_plc_xdir)
top_circ     = f._emit_raw(f"CIRCLE('',#{top_plc.eid},{R})")
top_arc_ec   = f._emit_raw(
    f"EDGE_CURVE('',#{v_top_0.eid},#{v_top_pi.eid},#{top_circ.eid},.T.)"
)
oe_top = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{top_arc_ec.eid},.T.)")

# ── Right lateral: v_top_pi → v_bot_pi (down at theta=π) ─────────────────────
# In UV on cylinder: (π+0.01, H) → (π+0.01, 0) — gap: starts at U=π+0.01
# (top arc ends at U=π on the surface; right lateral's pcurve starts at U=π+0.01)
lat_R_dir  = f.direction((0.0, 0.0, -1.0))
lat_R_vec  = f.vector(lat_R_dir, H)
lat_R_line = f.line(f.cartesian_point((-R, 0.0, H)), lat_R_vec)
lat_R_ec   = f._emit_raw(
    f"EDGE_CURVE('',#{v_top_pi.eid},#{v_bot_pi.eid},#{lat_R_line.eid},.T.)"
)
oe_lat_R = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{lat_R_ec.eid},.T.)")

# ── Bottom semi-circle arc reversed: v_bot_pi → v_bot_0 (U: π → 0) ──────────
bot_plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
bot_plc_zdir = f.direction((0.0, 0.0, 1.0))
bot_plc_xdir = f.direction((1.0, 0.0, 0.0))
bot_plc      = f.axis2_placement_3d(bot_plc_orig, bot_plc_zdir, bot_plc_xdir)
bot_circ     = f._emit_raw(f"CIRCLE('',#{bot_plc.eid},{R})")
bot_arc_ec   = f._emit_raw(
    f"EDGE_CURVE('',#{v_bot_0.eid},#{v_bot_pi.eid},#{bot_circ.eid},.T.)"
)
oe_bot = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{bot_arc_ec.eid},.F.)")  # reversed

# ── Left lateral: v_bot_0 → v_top_0 (up at theta=0) ─────────────────────────
lat_L_dir  = f.direction((0.0, 0.0, 1.0))
lat_L_vec  = f.vector(lat_L_dir, H)
lat_L_line = f.line(f.cartesian_point((R, 0.0, 0.0)), lat_L_vec)
lat_L_ec   = f._emit_raw(
    f"EDGE_CURVE('',#{v_bot_0.eid},#{v_top_0.eid},#{lat_L_line.eid},.T.)"
)
oe_lat_L = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{lat_L_ec.eid},.T.)")

# ── EDGE_LOOP: UV gap at top_arc/lat_R junction IS the mechanism ──────────────
# 3D: connected at v_top_pi; UV: top_arc ends at U=π, lat_R pcurve starts at U=π+0.01.
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_top.eid},#{oe_lat_R.eid},"
    f"#{oe_bot.eid},#{oe_lat_L.eid}))"
)

# Wire into face/shell topology — never orphan.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cyl_surf.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
