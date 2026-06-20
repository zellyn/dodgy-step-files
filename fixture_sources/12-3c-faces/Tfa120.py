"""Tfa120 — ShapeFix_Face.FixAddNaturalBound trimmed-conical.

Catalog claim: Natural boundary on trimmed CONICAL_SURFACE; FixAddNaturalBound
uses base surface parameter range, ignoring trim bounds. Without trim-context
preservation, FixAddNaturalBound reconstructs boundaries using untrimmed
surface domain.

Mechanism: OPEN_SHELL with a single CONICAL_SURFACE face trimmed to a partial
angular range (half-cone, u∈[0,π]) and a height range (v∈[1,3]).
FixAddNaturalBound adds natural bounds using the full cone domain [0,2π]×[0,∞)
instead of the trimmed [0,π]×[1,3] range. This is the defect: the natural
boundary reconstruction uses untrimmed surface parameters.

Geometry: Cone semi-angle = π/6 (30°), apex at origin. The face is a trapezoid
in 3D (half-conical frustum), bounded by:
  - Two slant edges along the seam (at u=0 and u=π, from v=1 to v=3)
  - A lower arc chord (at v=1 from u=0 to u=π through the y>0 half)
  - An upper arc chord (at v=3 from u=π to u=0 through the y>0 half)

The face IS on the live OPEN_SHELL traversal path.

Byte assertions:
  - contains(b'CONICAL_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa120",
    defect=(
        "OPEN_SHELL: CONICAL_SURFACE semi_angle=π/6, apex at origin; "
        "single face trimmed to half-cone u∈[0,π], v∈[1,3] (z from 1 to 3, y≥0); "
        "ShapeFix_Face::FixAddNaturalBound adds natural bounds using full cone "
        "domain [0,2π]×[0,∞) instead of trimmed [0,π]×[1,3]; "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# Cone: apex at origin, semi_angle = 30° = π/6
# At height z=v: radius = v * tan(π/6) ≈ v * 0.5774
ANGLE = _math.pi / 6.0   # semi-angle 30°
TAN_A = _math.tan(ANGLE)  # ≈ 0.5774

Z_LO = 1.0
Z_HI = 3.0
R_LO = Z_LO * TAN_A   # ≈ 0.5774
R_HI = Z_HI * TAN_A   # ≈ 1.7321

# Half-cone boundary points (seam at y=0, u=0 → x>0, u=π → x<0)
p_lo_xp = f.cartesian_point(( R_LO, 0.0, Z_LO))   # (u=0,  v=Z_LO)
p_lo_xm = f.cartesian_point((-R_LO, 0.0, Z_LO))   # (u=π, v=Z_LO)
p_hi_xp = f.cartesian_point(( R_HI, 0.0, Z_HI))   # (u=0,  v=Z_HI)
p_hi_xm = f.cartesian_point((-R_HI, 0.0, Z_HI))   # (u=π, v=Z_HI)

v_lo_xp = f.vertex_point(p_lo_xp)
v_lo_xm = f.vertex_point(p_lo_xm)
v_hi_xp = f.vertex_point(p_hi_xp)
v_hi_xm = f.vertex_point(p_hi_xm)

# Conical surface: apex at origin, axis along +z
cone_orig = f.cartesian_point((0.0, 0.0, 0.0))
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_plc  = f.axis2_placement_3d(cone_orig, cone_zdir, cone_xdir)
cone_surf = f.conical_surface(cone_plc, 0.0, ANGLE)

# Slant edges (along the cone surface, from low to high):
# Right seam (u=0): lo_xp → hi_xp
dx = R_HI - R_LO; dz = Z_HI - Z_LO
mag_slant = _math.sqrt(dx*dx + dz*dz)
e_right_slant = f.edge_curve(
    v_lo_xp, v_hi_xp,
    f.line(p_lo_xp, f.vector(f.direction((dx/mag_slant, 0.0, dz/mag_slant)), mag_slant))
)

# Left seam (u=π): hi_xm → lo_xm (going downward for CCW winding)
e_left_slant = f.edge_curve(
    v_hi_xm, v_lo_xm,
    f.line(p_hi_xm, f.vector(f.direction((dx/mag_slant, 0.0, -dz/mag_slant)), mag_slant))
)

# Lower arc chord (at z=Z_LO, from lo_xp to lo_xm through y>0)
mag_lo = 2.0 * R_LO
e_arc_lo = f.edge_curve(
    v_lo_xp, v_lo_xm,
    f.line(p_lo_xp, f.vector(f.direction((-1.0, 0.0, 0.0)), mag_lo))
)

# Upper arc chord (at z=Z_HI, from hi_xm to hi_xp through y>0)
mag_hi = 2.0 * R_HI
e_arc_hi = f.edge_curve(
    v_hi_xm, v_hi_xp,
    f.line(p_hi_xm, f.vector(f.direction((1.0, 0.0, 0.0)), mag_hi))
)

# Face boundary loop:
# lo_xp → hi_xp (right slant, going up)
# hi_xp ← hi_xm (upper arc reversed: hi_xm→hi_xp → reversed = hi_xp→hi_xm)
# Wait, let me track carefully:
# We need CCW from outward normal (which points away from z-axis for cone).
# Going: lo_xp → [right slant up] → hi_xp → [arc_hi reversed: hi_xp→hi_xm] → hi_xm
#       → [left slant: hi_xm→lo_xm] → lo_xm → [arc_lo reversed: lo_xm→lo_xp] → lo_xp
cone_loop = f.edge_loop([
    f.oriented_edge(e_right_slant, True),   # lo_xp → hi_xp
    f.oriented_edge(e_arc_hi,      False),  # hi_xp → hi_xm (arc reversed)
    f.oriented_edge(e_left_slant,  True),   # hi_xm → lo_xm
    f.oriented_edge(e_arc_lo,      False),  # lo_xm → lo_xp (arc reversed)
])
cone_face = f.advanced_face([f.face_outer_bound(cone_loop)], cone_surf)

# OPEN_SHELL: single face
open_sh = f.open_shell([cone_face])
sbsm    = f.shell_based_surface_model([open_sh])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa120.stp")
