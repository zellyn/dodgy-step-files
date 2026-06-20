"""Tfa071 — ShapeFix_Face.FixPeriodicDegenerated apex-curve direction.

Catalog claim: Conical face with apex below wire bounds. When apex V parameter
sits outside wire V-range and isUDecrease=false, apex curve direction and
conditional wire reversal produce inconsistent orientation. Wire reversal
triggered but apex curve construction does not account for actual wire topology.

Mechanism: CLOSED_SHELL with a CONICAL_SURFACE face and a bottom disc cap.
The cone has semi-angle ~0.52 rad, apex at V=-1 (outside the wire's V-range
of V=1..3). The outer wire wraps the conical face at V=1..3 with non-decreasing
U. FixPeriodicDegenerated applies apex curve construction and conditionally
reverses the wire when the apex is below the wire lower bound; but the apex
curve direction remains inconsistent with the reversed wire topology.

The cone: axis along Z, origin at (0,0,0), apex at (0,0,-1), radius at z=0
is tan(0.52)*1 ~ 0.572. Wire at V=1..3 means Z from 0 to 2.

Byte assertions:
  - contains(b'CONICAL_SURFACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa071",
    defect=(
        "CLOSED_SHELL: CONICAL_SURFACE face with semi-angle 0.52 rad; "
        "apex at V=-1 (below wire V-range); wire wraps cone at V=1..3 (Z=0..2); "
        "FixPeriodicDegenerated: apex below wire lower bound triggers wire reversal "
        "but apex curve direction not updated consistently — inconsistent orientation; "
        "seam EDGE_CURVE used .T. and .F. in same loop (full-revolution); "
        "bottom disc cap closes shell at z=0; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# Cone parameters
SEMI_ANGLE = 0.52   # radians, ~30 deg
# Apex at z = -1 (V = -1), below the wire's V-range of 1..3
# At z=0 (V=1), radius = tan(SEMI_ANGLE) * (0 - (-1)) = tan(0.52)*1
R_BOT = math.tan(SEMI_ANGLE) * 1.0   # radius at z=0 (V=1)
R_TOP = math.tan(SEMI_ANGLE) * 3.0   # radius at z=2 (V=3)
H = 2.0   # height of cone frustum (z=0 to z=2)

# ── Seam vertices ─────────────────────────────────────────────────────────────
pt_seam_bot = f.cartesian_point((R_BOT, 0.0, 0.0))
pt_seam_top = f.cartesian_point((R_TOP, 0.0, H))
v_seam_bot = f.vertex_point(pt_seam_bot)
v_seam_top = f.vertex_point(pt_seam_top)

# ── Seam edge: slant line along cone surface at U=0 ──────────────────────────
seam_dx = R_TOP - R_BOT
seam_len = math.sqrt(seam_dx**2 + H**2)
seam_dir = f.direction((seam_dx / seam_len, 0.0, H / seam_len))
seam_vec = f.vector(seam_dir, seam_len)
seam_line = f.line(pt_seam_bot, seam_vec)
seam_edge = f.edge_curve(v_seam_bot, v_seam_top, seam_line)

# ── Bottom circle at z=0 (V=1), radius R_BOT ─────────────────────────────────
bot_ctr = f.cartesian_point((0.0, 0.0, 0.0))
bot_ax  = f.direction((0.0, 0.0, -1.0))
bot_ref = f.direction((1.0, 0.0, 0.0))
bot_plc = f.axis2_placement_3d(bot_ctr, bot_ax, bot_ref)
bot_circle = f.circle(bot_plc, R_BOT)
bot_circle_edge = f.edge_curve(v_seam_bot, v_seam_bot, bot_circle)

# ── Top circle at z=H (V=3), radius R_TOP ────────────────────────────────────
top_ctr = f.cartesian_point((0.0, 0.0, H))
top_ax  = f.direction((0.0, 0.0,  1.0))
top_ref = f.direction((1.0, 0.0, 0.0))
top_plc = f.axis2_placement_3d(top_ctr, top_ax, top_ref)
top_circle = f.circle(top_plc, R_TOP)
top_circle_edge = f.edge_curve(v_seam_top, v_seam_top, top_circle)

# ── CONICAL_SURFACE: axis along Z, apex at (0,0,-1) ──────────────────────────
# Placement: origin at apex (0,0,-1), axis = +Z, ref = +X
cone_orig = f.cartesian_point((0.0, 0.0, -1.0))
cone_ax   = f.direction((0.0, 0.0, 1.0))
cone_ref  = f.direction((1.0, 0.0, 0.0))
cone_plc  = f.axis2_placement_3d(cone_orig, cone_ax, cone_ref)
cone_surf = f.conical_surface(cone_plc, 0.0, SEMI_ANGLE)

# ── Cone face: full-revolution frustum, V=1..3 ───────────────────────────────
# EDGE_LOOP: seam .T. (up), top_circle .T., seam .F. (down), bot_circle .F.
cone_loop = f.edge_loop([
    f.oriented_edge(seam_edge,        True),
    f.oriented_edge(top_circle_edge,  True),
    f.oriented_edge(seam_edge,        False),
    f.oriented_edge(bot_circle_edge,  False),
])
cone_fob  = f.face_outer_bound(cone_loop)
face_cone = f.advanced_face([cone_fob], cone_surf)

# ── Bottom disc cap at z=0 ────────────────────────────────────────────────────
bot_disc_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
bot_plane = f.plane(bot_disc_plc)
bot_disc_loop = f.edge_loop([f.oriented_edge(bot_circle_edge, True)])
bot_fob = f.face_outer_bound(bot_disc_loop)
face_bot = f.advanced_face([bot_fob], bot_plane)

# ── Top disc cap at z=H ───────────────────────────────────────────────────────
top_disc_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, H)),
    f.direction((0.0, 0.0,  1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
top_plane = f.plane(top_disc_plc)
top_disc_loop = f.edge_loop([f.oriented_edge(top_circle_edge, True)])
top_fob = f.face_outer_bound(top_disc_loop)
face_top = f.advanced_face([top_fob], top_plane)

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face_cone, face_bot, face_top])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa071.stp")
