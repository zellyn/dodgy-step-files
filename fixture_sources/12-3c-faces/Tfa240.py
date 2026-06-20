"""Tfa240 — ShapeFix_Face.Perform (line-346)

Integrated face-healing pipeline; mode-dependent cascade via base-slant-apex
decomposition on conical degenerate closure.

Mechanism: CLOSED_SHELL with TWO ADVANCED_FACEs forming a cone:
  face[0]: lateral surface on CONICAL_SURFACE; the face wire runs from the
    base circle up the seam line, then returns via the seam reversed, with the
    apex (degenerate) vertex. The conical closure is degenerate: the apex
    converges to a point (semi-angle=30°), requiring ShapeFix_Face::Perform()
    to cascade through the full integrated pipeline at line 346.
    Mode-dependent: depending on the healing mode bits, different sub-routines
    are activated: FixWires → FixOrientation → FixMissingSeam →
    FixPeriodicDegenerated → FixAddNaturalBound. The base-slant-apex topology
    triggers the apex-construction branch inside FixPeriodicDegenerated.
  face[1]: base disc cap on PLANE (bottom closure).

The integrated Perform() cascade is exercised because the conical seam requires
all healing sub-steps to process in mode-dependent order.

Byte assertions:
  - contains(b'CONICAL_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa240",
    defect=(
        "CLOSED_SHELL: TWO ADVANCED_FACEs forming a cone; "
        "face[0]: CONICAL_SURFACE semi_angle=30°, base_radius=2.0, apex at z=H; "
        "seam wire: base_circle(T) + seam_line(T) + seam_line(F); "
        "degenerate conical closure: apex convergence at seam; "
        "ShapeFix_Face::Perform (line 346): mode-dependent integrated cascade; "
        "pipeline: FixWires→FixOrientation→FixMissingSeam→FixPeriodicDegenerated"
        "→FixAddNaturalBound; apex-construction branch in FixPeriodicDegenerated; "
        "face[1]: PLANE base disc cap (bottom closure); "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

R = 2.0          # base radius
ANGLE_DEG = 30.0
ANGLE_RAD = _math.radians(ANGLE_DEG)
# H = R / tan(angle) — height of cone for given base radius and semi-angle
H = R / _math.tan(ANGLE_RAD)

# ── CONICAL_SURFACE: apex at top, base at z=0 ────────────────────────────────
# CONICAL_SURFACE(placement, bottom_radius, semi_angle)
# Axis along +Z, x-axis along +X; base radius R at z=0, apex at z=H
cone_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
cone_surf = f.conical_surface(cone_plc, R, ANGLE_RAD)

# ── Vertices ──────────────────────────────────────────────────────────────────
pt_base_seam = f.cartesian_point((R,   0.0, 0.0))   # seam on base circle
pt_apex      = f.cartesian_point((0.0, 0.0, H))     # apex (degenerate)

v_base = f.vertex_point(pt_base_seam)
v_apex = f.vertex_point(pt_apex)

# ── Seam edge: slant line from base to apex ───────────────────────────────────
dx = pt_apex.args[1][0] - pt_base_seam.args[1][0]   # = -R
dy = 0.0
dz = H
slant_len = _math.sqrt(dx*dx + dz*dz)
seam_line  = f.line(pt_base_seam,
                    f.vector(f.direction((dx/slant_len, 0.0, dz/slant_len)), slant_len))
seam_edge  = f.edge_curve(v_base, v_apex, seam_line)

# ── Base circle: full revolution at z=0, radius R ────────────────────────────
base_plc    = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
base_circle = f.circle(base_plc, R)
base_edge   = f.edge_curve(v_base, v_base, base_circle)  # degenerate: same vertex

# ── face[0]: conical lateral surface ─────────────────────────────────────────
# Wire: base_circle(T) + seam(T) + seam(F)
# seam used T then F: the dual-seam closure triggers FixPeriodicDegenerated
# apex-construction branch inside the full Perform() cascade.
cone_loop = f.edge_loop([
    f.oriented_edge(base_edge, True),
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(seam_edge, False),
])
face_cone = f.advanced_face([f.face_outer_bound(cone_loop)], cone_surf)

# ── face[1]: base disc cap on PLANE ──────────────────────────────────────────
base_plane_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, -1.0)),   # inward normal for bottom cap
    f.direction((1.0,  0.0, 0.0)),
)
base_plane = f.plane(base_plane_plc)
# Reuse base_edge (same circle) reversed for the cap — CCW from below
base_cap_loop = f.edge_loop([
    f.oriented_edge(base_edge, False),  # reversed: CCW from -Z direction
])
face_cap = f.advanced_face([f.face_outer_bound(base_cap_loop)], base_plane)

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ───────────────────────────────────────
closed_sh = f.closed_shell([face_cone, face_cap])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa240.stp")
