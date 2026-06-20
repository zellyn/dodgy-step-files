"""Tfa028 — Full-revolution CYLINDRICAL_SURFACE ADVANCED_FACE with single seam
EDGE_CURVE used twice (split_angle: angular span exceeds cap).

Catalog claim: A full-revolution CYLINDRICAL_SURFACE ADVANCED_FACE whose
FACE_OUTER_BOUND carries top and bottom CIRCLE EDGE_CURVEs with start==end
vertex (closed circular edges) plus a single seam EDGE_CURVE used twice in
the same EDGE_LOOP — once with .T. and once with .F. — instead of the two
split-seam halves a downstream consumer expects. Downstream meshers misbehave
on full-revolution faces; CAM tool-axis derivation expects per-segment.

Mechanism: CLOSED_SHELL built from one full-revolution cylindrical face plus
top and bottom disc caps.

The cylindrical face has:
  - seam edge: v_seam_bot → v_seam_top (used .T. and .F. in the same loop)
  - bottom circle: closed edge starting and ending at v_seam_bot (same vertex)
  - top circle: closed edge starting and ending at v_seam_top (same vertex)

Edge_loop for cylinder face: [seam .T., top_circle .T., seam .F., bot_circle .F.]

Full shell geometry:
  - cylinder radius=5, height=10, axis along Z, origin at (0,0,0)
  - v_seam_bot at (5,0,0); v_seam_top at (5,0,10)
  - seam_edge: v_seam_bot → v_seam_top (vertical line, .T. = upward, .F. = downward)
  - top_circle: center (0,0,10), radius 5, closed (start=end=v_seam_top)
  - bot_circle: center (0,0,0),  radius 5, closed (start=end=v_seam_bot)

Tier-3 assertions:
  face[0].surface_type == "cylinder"
  n_edges_total >= 4
  n_vertices_total >= 8
  brepcheck.valid == True

Expected: occt=shape(1)/shape(1) gmsh=shape(6) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa028",
    defect=(
        "CLOSED_SHELL: full-revolution CYLINDRICAL_SURFACE face (radius=5, height=10); "
        "seam EDGE_CURVE (v_seam_bot→v_seam_top, vertical) used TWICE in the same EDGE_LOOP "
        "— once .T. (upward) and once .F. (downward); "
        "top_circle and bot_circle are closed CIRCLE EDGE_CURVEs (start==end vertex); "
        "FACE_OUTER_BOUND loop: [seam .T., top_circle .T., seam .F., bot_circle .F.]; "
        "no split-seam halves — single seam spans full 2π; "
        "ShapeUpgrade_ShapeDivideAngle must subdivide at angular cap; "
        "defect IS on live cylindrical face traversal path"
    ),
)

R = 5.0
H = 10.0

# ── Seam vertices: at (R, 0, 0) and (R, 0, H) ───────────────────────────────
pt_seam_bot = f.cartesian_point((R, 0.0, 0.0))
pt_seam_top = f.cartesian_point((R, 0.0, H))

v_seam_bot = f.vertex_point(pt_seam_bot)
v_seam_top = f.vertex_point(pt_seam_top)

# ── Seam edge: vertical line from seam_bot to seam_top ───────────────────────
seam_dir  = f.direction((0.0, 0.0, 1.0))
seam_vec  = f.vector(seam_dir, H)
seam_line = f.line(pt_seam_bot, seam_vec)
seam_edge = f.edge_curve(v_seam_bot, v_seam_top, seam_line)

# ── Bottom circle: center (0,0,0), radius R, seam at (R,0,0) ─────────────────
# Axis: X-axis as ref, Z-axis up (pointing into circle from below = -Z for outward)
bot_ctr = f.cartesian_point((0.0, 0.0, 0.0))
bot_ax  = f.direction((0.0, 0.0, -1.0))   # axis points outward (downward) for bottom cap
bot_ref = f.direction((1.0, 0.0, 0.0))
bot_plc = f.axis2_placement_3d(bot_ctr, bot_ax, bot_ref)
bot_circle = f.circle(bot_plc, R)
# Closed circular edge: start == end == v_seam_bot
bot_circle_edge = f.edge_curve(v_seam_bot, v_seam_bot, bot_circle)

# ── Top circle: center (0,0,H), radius R, seam at (R,0,H) ───────────────────
top_ctr = f.cartesian_point((0.0, 0.0, H))
top_ax  = f.direction((0.0, 0.0,  1.0))   # axis points outward (upward) for top cap
top_ref = f.direction((1.0, 0.0, 0.0))
top_plc = f.axis2_placement_3d(top_ctr, top_ax, top_ref)
top_circle = f.circle(top_plc, R)
# Closed circular edge: start == end == v_seam_top
top_circle_edge = f.edge_curve(v_seam_top, v_seam_top, top_circle)

# ── CYLINDRICAL_SURFACE: axis along Z, origin (0,0,0), radius R ──────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_ax   = f.direction((0.0, 0.0, 1.0))
cyl_ref  = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_ax, cyl_ref)
cyl_surf = f.cylindrical_surface(cyl_plc, R)

# ── face[0]: full-revolution cylinder face ────────────────────────────────────
# EDGE_LOOP: seam .T. (up), top_circle .T., seam .F. (down), bot_circle .F.
# Reading around the face: start at v_seam_bot
#   seam .T.       : v_seam_bot → v_seam_top
#   top_circle .T. : v_seam_top → v_seam_top (full revolution CW from above)
#   seam .F.       : v_seam_top → v_seam_bot  (the defect: same seam, reversed)
#   bot_circle .F. : v_seam_bot → v_seam_bot (full revolution CW from below)
cyl_loop = f.edge_loop([
    f.oriented_edge(seam_edge,        True),   # up seam
    f.oriented_edge(top_circle_edge,  True),   # top circle (full revolution)
    f.oriented_edge(seam_edge,        False),  # down seam — DEFECT: same edge reused
    f.oriented_edge(bot_circle_edge,  False),  # bottom circle (reversed)
])
cyl_fob  = f.face_outer_bound(cyl_loop)
face_cyl = f.advanced_face([cyl_fob], cyl_surf)

# ── face[1]: bottom disc cap (z=0) ──────────────────────────────────────────
bot_disc_orig = f.cartesian_point((0.0, 0.0, 0.0))
bot_disc_ax   = f.direction((0.0, 0.0, -1.0))
bot_disc_ref  = f.direction((1.0, 0.0, 0.0))
bot_disc_plc  = f.axis2_placement_3d(bot_disc_orig, bot_disc_ax, bot_disc_ref)
bot_plane     = f.plane(bot_disc_plc)

bot_disc_loop = f.edge_loop([
    f.oriented_edge(bot_circle_edge, True),
])
bot_disc_fob  = f.face_outer_bound(bot_disc_loop)
face_bot      = f.advanced_face([bot_disc_fob], bot_plane)

# ── face[2]: top disc cap (z=H) ─────────────────────────────────────────────
top_disc_orig = f.cartesian_point((0.0, 0.0, H))
top_disc_ax   = f.direction((0.0, 0.0,  1.0))
top_disc_ref  = f.direction((1.0, 0.0, 0.0))
top_disc_plc  = f.axis2_placement_3d(top_disc_orig, top_disc_ax, top_disc_ref)
top_plane     = f.plane(top_disc_plc)

top_disc_loop = f.edge_loop([
    f.oriented_edge(top_circle_edge, True),
])
top_disc_fob  = f.face_outer_bound(top_disc_loop)
face_top      = f.advanced_face([top_disc_fob], top_plane)

# ── CLOSED_SHELL: cylinder + top + bottom ─────────────────────────────────────
closed_sh = f.closed_shell([face_cyl, face_bot, face_top])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa028.stp")
