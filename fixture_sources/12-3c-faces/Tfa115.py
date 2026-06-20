"""Tfa115 — ShapeFix_Face.FixPeriodicDegenerated revolution-axis edge.

Catalog claim: Surface of revolution where the rotation axis intersects the
face; FixPeriodicDegenerated misplaces the apex curve for the degenerate edge.
Revolution surfaces pinch to a line on the axis (at v=0). Edge construction and
orientation logic must distinguish this line-pinch from cone apex (point-pinch).

Mechanism: OPEN_SHELL with a single CYLINDRICAL_SURFACE face (approximating a
surface of revolution, radius 1.0, axis along z). The face boundary includes a
zero-length degenerate edge at the seam where all points collapse to the seam
line. FixPeriodicDegenerated must build the degenerate-edge apex curve along the
axis as a LINE, not as a point. The confusion arises because revolution surfaces
pinch to a LINE on the axis (line-pinch), unlike a cone whose apex is a point
(point-pinch).

The face is a rectangle in (u,v) parameter space:
  u ∈ [0, 2π] (full revolution), v ∈ [0, 2.0] (height from 0 to 2)
The seam edge at u=0/2π is where the degenerate edge arises.

Byte assertions:
  - contains(b'CYLINDRICAL_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa115",
    defect=(
        "OPEN_SHELL: CYLINDRICAL_SURFACE radius=1.0 axis along z; "
        "single face with seam edge at u=0/2π; "
        "seam is a zero-length degenerate edge (line-pinch) at v=bottom and v=top; "
        "ShapeFix_Face::FixPeriodicDegenerated must build degenerate apex curve along "
        "the axis as a LINE, not a point; confuses line-pinch (revolution) vs "
        "point-pinch (cone apex); defect IS on live OPEN_SHELL traversal path"
    ),
)

R = 1.0   # cylinder radius
H = 2.0   # height

# Cylindrical surface: axis along z, radius R
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf  = f.cylindrical_surface(cyl_plc, R)

# Seam points: at x=R, y=0, z=0 (bottom) and z=H (top)
p_bot = f.cartesian_point((R, 0.0, 0.0))
p_top = f.cartesian_point((R, 0.0, H))
v_bot = f.vertex_point(p_bot)
v_top = f.vertex_point(p_top)

# Seam edge (vertical, from bottom to top at x=R, y=0)
seam_dir = f.direction((0.0, 0.0, 1.0))
seam_vec = f.vector(seam_dir, H)
e_seam   = f.edge_curve(v_bot, v_top, f.line(p_bot, seam_vec))

# Bottom degenerate edge (zero-length, at v=0 of the revolution surface)
# This represents the line-pinch at the bottom circle
p_bot2 = f.cartesian_point((R, 0.0, 0.0))
v_bot2 = f.vertex_point(p_bot2)
zero_dir = f.direction((1.0, 0.0, 0.0))
zero_vec = f.vector(zero_dir, 0.0)
e_bot_degen = f.edge_curve(v_bot, v_bot2, f.line(p_bot, zero_vec))

# Top degenerate edge (zero-length, at v=H)
p_top2 = f.cartesian_point((R, 0.0, H))
v_top2 = f.vertex_point(p_top2)
e_top_degen = f.edge_curve(v_top, v_top2, f.line(p_top, zero_vec))

# Face loop: traverse the cylindrical face boundary
# Going: bot → seam up → top_degen → seam_back_down → bot_degen
# Must form a closed loop on the cylinder:
#   v_bot → [seam] → v_top → [top_degen] → v_top2 → [seam False] → v_bot2 → [bot_degen False] → v_bot
# Simplified: use 4-edge loop: seam_up, top_degen, seam_down, bot_degen
face_loop = f.edge_loop([
    f.oriented_edge(e_seam,      True),   # v_bot → v_top (up the seam)
    f.oriented_edge(e_top_degen, True),   # v_top → v_top2 (zero-length at top)
    f.oriented_edge(e_seam,      False),  # v_top2 ← v_bot2 (reversed, but v_top2==v_top)
    f.oriented_edge(e_bot_degen, False),  # v_bot2 ← v_bot (reversed zero-length)
])
cyl_face = f.advanced_face([f.face_outer_bound(face_loop)], cyl_surf)

# OPEN_SHELL: single face
open_sh = f.open_shell([cyl_face])
sbsm    = f.shell_based_surface_model([open_sh])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa115.stp")
