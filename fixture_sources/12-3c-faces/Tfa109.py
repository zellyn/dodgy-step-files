"""Tfa109 — Obtuse-angle pin misclassification.

Catalog claim: Pin face whose tip angle exceeds 90° (actually a wedge).
CheckPin's threshold flags it as a pin when other dimensions are small,
because the algorithm doesn't validate that the tip is actually acute.

Mechanism: MANIFOLD_SOLID_BREP with a single thin-wedge face (planar triangle
with obtuse tip angle ~120°) that is small enough to pass dimensional thresholds
but whose tip angle fails acuteness test. ShapeAnalysis_CheckSmallFace::CheckPin
checks small area and narrow bounding dimensions but does NOT verify tip
acuteness; it returns true (is-pin) based on geometry alone without angle
validation. The wedge face IS on the live CLOSED_SHELL traversal path.

Geometry: Isosceles triangle with base 0.2 (short, small-face dimension) and
height 0.05 (very narrow), giving a wide, flat shape. The tip angle at the apex
is approximately 2*atan(0.1/0.05) ≈ 126° — well above 90°. A companion square
face (1×1) closes the shell as a flat back wall.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'CLOSED_SHELL')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa109",
    defect=(
        "CLOSED_SHELL: thin triangular wedge ADVANCED_FACE at z=0 with obtuse tip angle "
        "~126° (base 0.2, height 0.05); "
        "ShapeAnalysis_CheckSmallFace::CheckPin checks small area and narrow dimensions "
        "but does NOT validate tip acuteness; flags as pin even though tip > 90°; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# Wedge (obtuse-tip triangle) geometry at z=0
# Base vertices at y=0, apex at y=0.05 (narrow height)
# Base half-width = 0.1, so base = 0.2
# Tip angle = 2 * atan(0.1 / 0.05) ≈ 126° — obtuse
p_apex  = f.cartesian_point((0.0,   0.05, 0.0))
p_bl    = f.cartesian_point((-0.1,  0.0,  0.0))
p_br    = f.cartesian_point(( 0.1,  0.0,  0.0))

v_apex  = f.vertex_point(p_apex)
v_bl    = f.vertex_point(p_bl)
v_br    = f.vertex_point(p_br)

# Edges: base (bl→br), right leg (br→apex), left leg (apex→bl)
dx_base = 0.2
e_base = f.edge_curve(v_bl, v_br, f.line(p_bl, f.vector(f.direction(( 1.0, 0.0, 0.0)), dx_base)))

dx_r = 0.1; dy_r = -0.05
mag_r = _math.sqrt(dx_r*dx_r + dy_r*dy_r)
e_right = f.edge_curve(v_br, v_apex, f.line(p_br,
    f.vector(f.direction((dx_r/mag_r, dy_r/mag_r, 0.0)), mag_r)))

dx_l = -0.1; dy_l = 0.05
mag_l = _math.sqrt(dx_l*dx_l + dy_l*dy_l)
e_left = f.edge_curve(v_apex, v_bl, f.line(p_apex,
    f.vector(f.direction((dx_l/mag_l, dy_l/mag_l, 0.0)), mag_l)))

# Loop: bl→br (base .T.), br→apex (right .T.), apex→bl (left .T.) — CCW from +Z side
wedge_loop = f.edge_loop([
    f.oriented_edge(e_base,  True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_left,  True),
])

wedge_orig = f.cartesian_point((0.0, 0.0, 0.0))
wedge_zdir = f.direction((0.0, 0.0, 1.0))
wedge_xdir = f.direction((1.0, 0.0, 0.0))
wedge_plc  = f.axis2_placement_3d(wedge_orig, wedge_zdir, wedge_xdir)
wedge_face = f.advanced_face([f.face_outer_bound(wedge_loop)], f.plane(wedge_plc))

# Build a watertight triangular prism (depth 0.1) so shape(1) loads cleanly.
# Front = wedge triangle at z=0, Back = matching triangle at z=-0.1, 3 side walls.

p_apex_b  = f.cartesian_point((0.0,   0.05, -0.1))
p_bl_b    = f.cartesian_point((-0.1,  0.0,  -0.1))
p_br_b    = f.cartesian_point(( 0.1,  0.0,  -0.1))

v_apex_b  = f.vertex_point(p_apex_b)
v_bl_b    = f.vertex_point(p_bl_b)
v_br_b    = f.vertex_point(p_br_b)

# Back face edges (reversed winding for outward normal)
e_base_b  = f.edge_curve(v_bl_b, v_br_b, f.line(p_bl_b, f.vector(f.direction((1.0, 0.0, 0.0)), 0.2)))
e_right_b = f.edge_curve(v_br_b, v_apex_b, f.line(p_br_b,
    f.vector(f.direction((dx_r/mag_r, dy_r/mag_r, 0.0)), mag_r)))
e_left_b  = f.edge_curve(v_apex_b, v_bl_b, f.line(p_apex_b,
    f.vector(f.direction((dx_l/mag_l, dy_l/mag_l, 0.0)), mag_l)))

back_loop = f.edge_loop([
    f.oriented_edge(e_base_b,  False),
    f.oriented_edge(e_right_b, False),
    f.oriented_edge(e_left_b,  False),
])
back_orig = f.cartesian_point((0.0, 0.0, -0.1))
back_zdir = f.direction((0.0, 0.0, -1.0))
back_xdir = f.direction((1.0, 0.0, 0.0))
back_face = f.advanced_face([f.face_outer_bound(back_loop)], f.plane(
    f.axis2_placement_3d(back_orig, back_zdir, back_xdir)))

# Side walls: vertical edges connecting front to back
ev_bl    = f.edge_curve(v_bl,    v_bl_b,    f.line(p_bl,    f.vector(f.direction((0.0, 0.0, -1.0)), 0.1)))
ev_br    = f.edge_curve(v_br,    v_br_b,    f.line(p_br,    f.vector(f.direction((0.0, 0.0, -1.0)), 0.1)))
ev_apex  = f.edge_curve(v_apex,  v_apex_b,  f.line(p_apex,  f.vector(f.direction((0.0, 0.0, -1.0)), 0.1)))

# Bottom side (y=0, base edge)
bot_side_loop = f.edge_loop([
    f.oriented_edge(e_base,  True),
    f.oriented_edge(ev_br,   True),
    f.oriented_edge(e_base_b, False),
    f.oriented_edge(ev_bl,   False),
])
bot_side_orig = f.cartesian_point((-0.1, 0.0, 0.0))
bot_side_zdir = f.direction((0.0, -1.0, 0.0))
bot_side_xdir = f.direction((1.0,  0.0, 0.0))
bot_side_face = f.advanced_face([f.face_outer_bound(bot_side_loop)], f.plane(
    f.axis2_placement_3d(bot_side_orig, bot_side_zdir, bot_side_xdir)))

# Right side (br→apex edge)
rgt_side_loop = f.edge_loop([
    f.oriented_edge(e_right,   True),
    f.oriented_edge(ev_apex,   True),
    f.oriented_edge(e_right_b, False),
    f.oriented_edge(ev_br,     False),
])
# normal points outward: perpendicular to (dx_r, dy_r)
# Normal = (dy_r, -dx_r) = (-0.05, -0.1) → normalize → (-0.447, -0.894)
nx_r = dy_r / mag_r; ny_r = -dx_r / mag_r
rgt_side_orig = f.cartesian_point((0.1, 0.0, 0.0))
rgt_side_zdir = f.direction((nx_r, ny_r, 0.0))
rgt_side_xdir = f.direction((dx_r/mag_r, dy_r/mag_r, 0.0))
rgt_side_face = f.advanced_face([f.face_outer_bound(rgt_side_loop)], f.plane(
    f.axis2_placement_3d(rgt_side_orig, rgt_side_zdir, rgt_side_xdir)))

# Left side (apex→bl edge)
lft_side_loop = f.edge_loop([
    f.oriented_edge(e_left,   True),
    f.oriented_edge(ev_bl,    True),
    f.oriented_edge(e_left_b, False),
    f.oriented_edge(ev_apex,  False),
])
nx_l = -dy_l / mag_l; ny_l = dx_l / mag_l
lft_side_orig = f.cartesian_point((-0.1, 0.0, 0.0))
lft_side_zdir = f.direction((nx_l, ny_l, 0.0))
lft_side_xdir = f.direction((dx_l/mag_l, dy_l/mag_l, 0.0))
lft_side_face = f.advanced_face([f.face_outer_bound(lft_side_loop)], f.plane(
    f.axis2_placement_3d(lft_side_orig, lft_side_zdir, lft_side_xdir)))

# ── CLOSED_SHELL → MANIFOLD_SOLID_BREP ──────────────────────────────────────────
closed_sh = f.closed_shell([wedge_face, back_face, bot_side_face, rgt_side_face, lft_side_face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa109.stp")
