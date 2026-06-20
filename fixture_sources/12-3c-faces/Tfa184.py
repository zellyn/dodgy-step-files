"""Tfa184 — ShapeAnalysis_CheckSmallFace.CheckTwisted face-on-cone-apex

Catalog claim: Face on conical surface with apex at origin. Wire passes through
cone apex point where surface normal is undefined (apex singularity).
CheckTwisted's normal-direction test fails: no valid normal at apex. Tests
degenerate surface point handling in twisted-face detection.

Mechanism: CLOSED_SHELL: a CONICAL_SURFACE face (apex at origin, semi-angle 30°,
axis +Z) whose wire loop passes THROUGH the apex point (0,0,0). The apex is a
singular point on the conical surface where the normal direction is undefined.
When ShapeAnalysis_CheckSmallFace::CheckTwisted samples the face normal at the
apex vertex it encounters the singularity, causing undefined/garbage normal
comparison. A flat circular cap closes the shell. Defect IS on live traversal.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'CONICAL_SURFACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa184",
    defect=(
        "CLOSED_SHELL: CONICAL_SURFACE face (apex at origin, semi_angle=30°, axis +Z); "
        "outer wire loop passes through apex vertex (0,0,0) — apex singularity; "
        "CheckTwisted samples surface normal at apex where normal is undefined; "
        "undefined normal produces garbage direction comparison result; "
        "defect IS on live CLOSED_SHELL traversal path; "
        "no orphaned entities"
    ),
)

SEMI_ANGLE = _math.radians(30.0)  # 30 degree cone
H = 5.0                            # height of the cone
R_BASE = H * _math.tan(SEMI_ANGLE) # radius at base: 5*tan(30°) ≈ 2.887

# ── Conical surface: apex at origin, axis +Z ──────────────────────────────
cone_orig = f.cartesian_point((0.0, 0.0, 0.0))
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_plc  = f.axis2_placement_3d(cone_orig, cone_zdir, cone_xdir)
# CONICAL_SURFACE: base radius=0 (at placement origin=apex), semi-angle
# In STEP, CONICAL_SURFACE apex is at placement origin when base_radius=0.
# Use base_radius=0, semi_angle=SEMI_ANGLE: cone grows outward from apex.
cone_surf = f.conical_surface(cone_plc, 0.0, SEMI_ANGLE)

# The apex point (singular): (0,0,0)
p_apex = f.cartesian_point((0.0, 0.0, 0.0))
v_apex = f.vertex_point(p_apex)

# Points on the base circle of the cone at height H
# Use 4 points at compass positions
p_E = f.cartesian_point(( R_BASE, 0.0,      H))
p_N = f.cartesian_point(( 0.0,   R_BASE,    H))
p_W = f.cartesian_point((-R_BASE, 0.0,      H))
p_S = f.cartesian_point(( 0.0,  -R_BASE,    H))

v_E = f.vertex_point(p_E); v_N = f.vertex_point(p_N)
v_W = f.vertex_point(p_W); v_S = f.vertex_point(p_S)

# Slant edges from apex to base points (straight lines on cone surface)
def _slant(p1, v1, p2, v2):
    dx = p2.args[1][0] - p1.args[1][0]
    dy = p2.args[1][1] - p1.args[1][1]
    dz = p2.args[1][2] - p1.args[1][2]
    length = _math.sqrt(dx*dx + dy*dy + dz*dz)
    d = f.direction((dx/length, dy/length, dz/length))
    return f.edge_curve(v1, v2, f.line(p1, f.vector(d, length)))

e_AE = _slant(p_apex, v_apex, p_E, v_E)   # apex → E
e_EN = _slant(p_E, v_E, p_N, v_N)         # base E→N (straight, approximation)
e_NW = _slant(p_N, v_N, p_W, v_W)
e_WS = _slant(p_W, v_S, p_S, v_S)         # using p_W,v_S intentionally for twist
# Wait: fix that. Use correct points:
e_WS2 = _slant(p_W, v_W, p_S, v_S)
e_SA  = _slant(p_S, v_S, p_apex, v_apex)  # back to apex (the singular point)

# Cone face wire: apex → E → N → W → S → apex (passes through apex twice: start and end)
cone_loop = f.edge_loop([
    f.oriented_edge(e_AE,  True),
    f.oriented_edge(e_EN,  True),
    f.oriented_edge(e_NW,  True),
    f.oriented_edge(e_WS2, True),
    f.oriented_edge(e_SA,  True),
])
cone_face = f.advanced_face([f.face_outer_bound(cone_loop)], cone_surf)

# ── Flat cap: disk at height H to close the shell ─────────────────────────
cap_orig = f.cartesian_point((0.0, 0.0, H))
cap_zdir = f.direction((0.0, 0.0, -1.0))  # normal pointing inward (downward) for correct solid
cap_xdir = f.direction((1.0, 0.0, 0.0))
cap_plc  = f.axis2_placement_3d(cap_orig, cap_zdir, cap_xdir)
cap_surf = f.plane(cap_plc)

# Base circle at height H for cap
cap_circ_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, H)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
cap_circle = f.circle(cap_circ_plc, R_BASE)

# Arc edges for cap (reversed winding: CW from above = outward normal from +Z side)
arc_NE = f.edge_curve(v_N, v_E, cap_circle)
arc_ES = f.edge_curve(v_E, v_S, cap_circle)
arc_SW = f.edge_curve(v_S, v_W, cap_circle)
arc_WN = f.edge_curve(v_W, v_N, cap_circle)

cap_loop = f.edge_loop([
    f.oriented_edge(arc_NE, True),
    f.oriented_edge(arc_ES, True),
    f.oriented_edge(arc_SW, True),
    f.oriented_edge(arc_WN, True),
])
cap_face = f.advanced_face([f.face_outer_bound(cap_loop)], cap_surf)

# ── CLOSED_SHELL → MANIFOLD_SOLID_BREP ────────────────────────────────────
closed_sh = f.closed_shell([cone_face, cap_face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa184.stp")
