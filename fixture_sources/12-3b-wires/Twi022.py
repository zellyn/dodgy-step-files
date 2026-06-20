"""Twi022 — Seam edge with swapped or duplicated pcurves on a periodic face.

Catalog claim: A seam edge on a periodic CYLINDRICAL_SURFACE face carries two
pcurves; one for the U=0 side and one for the U=period (2π) side. The input
assigns the same PCURVE to both slots (duplicated), so the UV closure step of
one full period is missing; the wire fails to close in UV parameter space.

Mechanism IS the SEAM_CURVE whose two associated_geometry slots reference the
same PCURVE entity (same entity ID used twice): the seam EDGE_CURVE is built
from a SEAM_CURVE where both pcurve references are identical, giving a UV
step of zero instead of 2π. The defect SEAM_CURVE IS referenced via
EDGE_CURVE → ORIENTED_EDGE → EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE →
OPEN_SHELL; never orphaned.

Reproducer: SEAM_CURVE referencing the same PCURVE for both associated_geometry
slots, causing missing period shift on the periodic face.

Byte assertions:
  - count_entity_def(b'SEAM_CURVE') == 1
  - count_entity_def(b'CYLINDRICAL_SURFACE') == 1

Tier-3 assertions:
  - n_edges_total >= 2
  - face[0].surface_type == "cylinder"
  - n_vertices_total >= 4

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi022",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a CYLINDRICAL_SURFACE (radius 1, height 2); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with two horizontal arcs (top and bottom) "
        "and one SEAM_CURVE whose both associated_geometry slots reference the SAME PCURVE; "
        "duplicated (same-entity) pcurve in SEAM_CURVE IS the mechanism — missing period shift; "
        "SEAM_CURVE IS wired into EDGE_CURVE, ORIENTED_EDGE, EDGE_LOOP, FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; "
        "kernel must detect missing period shift and shift one pcurve by 2π or reject as malformed"
    ),
)

# ── CYLINDRICAL_SURFACE: axis +Z, radius 1 ───────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('',#{cyl_plc.eid},1.0)")

# ── Shared seam vertex at (1,0) at z=0 and z=2 ───────────────────────────────
v_bot = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
v_top = f.vertex_point(f.cartesian_point((1.0, 0.0, 2.0)))

# ── 3D LINE for seam (from z=0 to z=2 at x=1,y=0) ───────────────────────────
seam_3d_dir = f.direction((0.0, 0.0, 1.0))
seam_3d_vec = f.vector(seam_3d_dir, 2.0)
seam_3d_line = f.line(f.cartesian_point((1.0, 0.0, 0.0)), seam_3d_vec)

# ── PCURVE: a vertical line at U=0 in (U,V) parameter space of the cylinder ──
# On a cylinder, U=azimuth, V=height. Seam at U=0 runs from V=0 to V=2.
uv_orig_U0 = f.cartesian_point((0.0, 0.0))
uv_dir_U0  = f.direction((0.0, 1.0))    # direction in UV: +V
uv_vec_U0  = f.vector(uv_dir_U0, 2.0)
uv_line_U0 = f._emit_raw(
    f"LINE('',#{uv_orig_U0.eid},#{uv_vec_U0.eid})"
)
# DEFINITIONAL_REPRESENTATION for the pcurve
surf_ref = cyl_surf  # reference to the surface
drep_U0 = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{uv_line_U0.eid}),#?)"
)
# Use _emit_raw to build the PCURVE directly since step_builder may not have pcurve()
# PCURVE('', surface_ref, definitional_rep) — both slots will reference pcurve_U0.
# We'll use a simpler approach: emit the PCURVE pointing to the surface and 2D rep.
# Build a second (identical) definitional rep so the two pcurve slots are visually same:
uv_orig_U0b = f.cartesian_point((0.0, 0.0))
uv_dir_U0b  = f.direction((0.0, 1.0))
uv_vec_U0b  = f.vector(uv_dir_U0b, 2.0)
uv_line_U0b = f._emit_raw(
    f"LINE('',#{uv_orig_U0b.eid},#{uv_vec_U0b.eid})"
)
drep_U0b = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{uv_line_U0b.eid}),#?)"
)

# PCURVE entities
pcurve_U0  = f._emit_raw(f"PCURVE('',#{cyl_surf.eid},#{drep_U0.eid})")
# For the duplicated-pcurve defect we emit BOTH slots pointing at pcurve_U0:
pcurve_dup = pcurve_U0   # same entity — this IS the defect

# ── SEAM_CURVE: both associated_geometry = same PCURVE — IS the mechanism ────
seam_curve = f._emit_raw(
    f"SEAM_CURVE('',#{seam_3d_line.eid},"
    f"(#{pcurve_U0.eid},#{pcurve_dup.eid}),.PCURVE_S1.)"
)

# EDGE_CURVE wrapping the SEAM_CURVE
seam_edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_bot.eid},#{v_top.eid},#{seam_curve.eid},.T.)"
)
seam_oe_fwd = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{seam_edge.eid},.T.)")
seam_oe_rev = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{seam_edge.eid},.F.)")

# ── Top circle: full 360° at z=2 ─────────────────────────────────────────────
v_top_seam = f.vertex_point(f.cartesian_point((1.0, 0.0, 2.0)))
top_plc_orig = f.cartesian_point((0.0, 0.0, 2.0))
top_plc_zdir = f.direction((0.0, 0.0, 1.0))
top_plc_xdir = f.direction((1.0, 0.0, 0.0))
top_plc  = f.axis2_placement_3d(top_plc_orig, top_plc_zdir, top_plc_xdir)
top_circ = f._emit_raw(f"CIRCLE('',#{top_plc.eid},1.0)")
top_edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_top.eid},#{v_top_seam.eid},#{top_circ.eid},.T.)"
)
top_oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{top_edge.eid},.T.)")

# ── Bottom circle: full 360° at z=0 ──────────────────────────────────────────
v_bot_seam = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
bot_plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
bot_plc_zdir = f.direction((0.0, 0.0, 1.0))
bot_plc_xdir = f.direction((1.0, 0.0, 0.0))
bot_plc  = f.axis2_placement_3d(bot_plc_orig, bot_plc_zdir, bot_plc_xdir)
bot_circ = f._emit_raw(f"CIRCLE('',#{bot_plc.eid},1.0)")
bot_edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_bot_seam.eid},#{v_bot.eid},#{bot_circ.eid},.T.)"
)
bot_oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{bot_edge.eid},.F.)")

# ── EDGE_LOOP: seam edge with duplicated pcurve IS the mechanism ──────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{bot_oe.eid},#{seam_oe_fwd.eid},"
    f"#{top_oe.eid},#{seam_oe_rev.eid}))"
)

# Wire into face/shell topology — never orphan.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cyl_surf.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
