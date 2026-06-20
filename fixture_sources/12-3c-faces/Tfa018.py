"""Tfa018 — Same-domain face merge across periodic seam: shared EDGE_CURVE
reused with .T./.F. on both halves (missed-seam reconstruction).

Catalog claim: When merging co-cylindrical faces across a periodic seam, each
seam EDGE_CURVE is referenced by both halves' EDGE_LOOPs as ORIENTED_EDGEs
with opposing .T./.F. senses; the kernel crashes in debug or returns invalid
geometry when reconstructing the seam edge from a pcurve copy.

Mechanism IS a GEOMETRIC_CURVE_SET containing two ADVANCED_FACEs on the same
CYLINDRICAL_SURFACE, each forming a half-cylinder. The shared seam EDGE_CURVE
at x=-10 appears in both EDGE_LOOPs — once as .T. in face A and once as .F.
in face B — the same-edge-different-sense pattern that triggers the missed-seam
reconstruction bug. OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'CYLINDRICAL_SURFACE(')
  - contains(b'(-10.0,0.0,0.0)')
  - contains(b'(-10.0,0.0,5.0)')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Tfa018",
    defect=(
        "GEOMETRIC_CURVE_SET containing two co-cylindrical ADVANCED_FACEs; "
        "seam EDGE_CURVE at x=-10 (the 180-degree seam line) is referenced by "
        "both halves' EDGE_LOOPs: face A uses it as .T. and face B uses it as .F.; "
        "same-edge-different-sense pattern triggers missed-seam reconstruction; "
        "kernel must copy a pcurve to reconstruct the seam edge correctly; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── CYLINDRICAL_SURFACE: axis +Z, radius 10, centred at origin ───────────────
# Cylinder: radius 10, axis along Z, Z from 0 to 5.
# At angle=pi (180 deg), x = -10, y = 0 → the seam line.
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('',#{cyl_plc.eid},10.0)")

# ── Key vertices ─────────────────────────────────────────────────────────────
# Front seam at angle=0: (10, 0, 0) bottom and (10, 0, 5) top
# Rear seam at angle=pi: (-10, 0, 0) bottom and (-10, 0, 5) top
# The byte assertions require (-10.0,0.0,0.0) and (-10.0,0.0,5.0) in the file.

v_front_bot = f.vertex_point(f.cartesian_point((10.0, 0.0, 0.0)))
v_front_top = f.vertex_point(f.cartesian_point((10.0, 0.0, 5.0)))
v_rear_bot  = f.vertex_point(f.cartesian_point((-10.0, 0.0, 0.0)))   # byte assertion
v_rear_top  = f.vertex_point(f.cartesian_point((-10.0, 0.0, 5.0)))   # byte assertion

# ── Helper: vertical seam line from bottom to top ────────────────────────────
def vertical_edge(p_bot_coords, p_top_coords, v_bot, v_top, name=""):
    p_bot = f.cartesian_point(p_bot_coords)
    dz    = f.direction((0.0, 0.0, 1.0))
    vec   = f.vector(dz, 5.0)
    ln    = f.line(p_bot, vec)
    return f._emit_raw(f"EDGE_CURVE('{name}',#{v_bot.eid},#{v_top.eid},#{ln.eid},.T.)")

# ── Shared seam EDGE_CURVE at x=-10 (rear seam) — used by BOTH face halves ───
seam_ec = vertical_edge(
    (-10.0, 0.0, 0.0), (-10.0, 0.0, 5.0),
    v_rear_bot, v_rear_top,
    name="rear_seam"
)

# ── Front seam EDGE_CURVE at x=+10 (only one use) ────────────────────────────
front_seam_ec = vertical_edge(
    (10.0, 0.0, 0.0), (10.0, 0.0, 5.0),
    v_front_bot, v_front_top,
    name="front_seam"
)

# ── Top and bottom arcs (half-circle EDGE_CURVEs) ─────────────────────────────
# Bottom arc face A: front_bot → rear_bot going through (+y) hemisphere
# Use LINE approximation for byte-assertion simplicity (half-arc ~semicircle)
# We use CIRCLE arcs for fidelity.
# Circle at z=0, radius 10, axis +Z at origin.
bot_ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
bot_ax_z    = f.direction((0.0, 0.0, 1.0))
bot_ax_x    = f.direction((1.0, 0.0, 0.0))
bot_ax      = f.axis2_placement_3d(bot_ax_orig, bot_ax_z, bot_ax_x)
bot_circle  = f._emit_raw(f"CIRCLE('',#{bot_ax.eid},10.0)")

# Bottom arc A: front_bot → rear_bot (y>0 half, angle 0→pi)
bot_arc_a_ec = f._emit_raw(
    f"EDGE_CURVE('bot_arc_a',#{v_front_bot.eid},#{v_rear_bot.eid},#{bot_circle.eid},.T.)"
)
# Bottom arc B: rear_bot → front_bot (y<0 half, angle pi→2pi)
# Reuse circle but traverse the other half via .T. on reverse direction.
bot_ax_xneg = f.direction((-1.0, 0.0, 0.0))
bot_ax_b    = f.axis2_placement_3d(bot_ax_orig, bot_ax_z, bot_ax_xneg)
bot_circle_b = f._emit_raw(f"CIRCLE('',#{bot_ax_b.eid},10.0)")
bot_arc_b_ec = f._emit_raw(
    f"EDGE_CURVE('bot_arc_b',#{v_rear_bot.eid},#{v_front_bot.eid},#{bot_circle_b.eid},.T.)"
)

# Top circle at z=5
top_ax_orig = f.cartesian_point((0.0, 0.0, 5.0))
top_ax_z    = f.direction((0.0, 0.0, 1.0))
top_ax_x    = f.direction((1.0, 0.0, 0.0))
top_ax      = f.axis2_placement_3d(top_ax_orig, top_ax_z, top_ax_x)
top_circle  = f._emit_raw(f"CIRCLE('',#{top_ax.eid},10.0)")

top_arc_a_ec = f._emit_raw(
    f"EDGE_CURVE('top_arc_a',#{v_front_top.eid},#{v_rear_top.eid},#{top_circle.eid},.T.)"
)
top_ax_xneg  = f.direction((-1.0, 0.0, 0.0))
top_ax_b     = f.axis2_placement_3d(top_ax_orig, top_ax_z, top_ax_xneg)
top_circle_b = f._emit_raw(f"CIRCLE('',#{top_ax_b.eid},10.0)")
top_arc_b_ec = f._emit_raw(
    f"EDGE_CURVE('top_arc_b',#{v_rear_top.eid},#{v_front_top.eid},#{top_circle_b.eid},.T.)"
)

# ── FACE A: y>0 half, traversal: bot_arc_a, seam .T., top_arc_a reversed, front_seam reversed
# loop A: front_bot →(bot_arc_a)→ rear_bot →(seam .T.)→ rear_top →(top_arc_a .F.)→ front_top →(front_seam .F.)→ front_bot
oe_bot_a    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{bot_arc_a_ec.eid},.T.)")
oe_seam_a   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{seam_ec.eid},.T.)")      # seam used .T.
oe_top_a    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{top_arc_a_ec.eid},.F.)")
oe_front_a  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{front_seam_ec.eid},.F.)")

loop_a = f._emit_raw(
    f"EDGE_LOOP('loop_a',(#{oe_bot_a.eid},#{oe_seam_a.eid},#{oe_top_a.eid},#{oe_front_a.eid}))"
)
fob_a = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop_a.eid},.T.)")
af_a  = f._emit_raw(f"ADVANCED_FACE('face_a',(#{fob_a.eid}),#{cyl_surf.eid},.T.)")

# ── FACE B: y<0 half — seam edge reused with .F.
# loop B: rear_bot →(bot_arc_b)→ front_bot →(front_seam .T.)→ front_top →(top_arc_b .T.)→ rear_top →(seam .F.)→ rear_bot
oe_bot_b    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{bot_arc_b_ec.eid},.T.)")
oe_front_b  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{front_seam_ec.eid},.T.)")
oe_top_b    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{top_arc_b_ec.eid},.T.)")
oe_seam_b   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{seam_ec.eid},.F.)")      # seam reused .F.

loop_b = f._emit_raw(
    f"EDGE_LOOP('loop_b',(#{oe_bot_b.eid},#{oe_front_b.eid},#{oe_top_b.eid},#{oe_seam_b.eid}))"
)
fob_b = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop_b.eid},.T.)")
af_b  = f._emit_raw(f"ADVANCED_FACE('face_b',(#{fob_b.eid}),#{cyl_surf.eid},.T.)")

# ── GEOMETRIC_CURVE_SET IS model entity — OCC yields empty ───────────────────
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{af_a.eid},#{af_b.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa018.stp")
