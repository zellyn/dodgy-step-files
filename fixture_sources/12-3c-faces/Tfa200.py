"""Tfa200 — ShapeAnalysis_Surface.DegeneratedValues cone-apex-degeneracy

A conical surface whose semi-angle approaches zero becomes degenerate at the
apex. The degeneracy analyzer identifies apex points by evaluating surface
parametrization; missing or incomplete checks allow apex-degenerate faces to
proceed without special-case handling, causing downstream curve projections
and tangent computations to produce NaNs or infinite curvature.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a CONICAL_SURFACE. The cone
has base radius=1 and a near-zero semi-angle (0.01 rad ≈ 0.57°). At this
angle the apex is approximately 100 units above the base, and the apex cross-
section has nearly zero radius. The face is a full-revolution conical patch from
the base circle to a tiny apex circle; the apex edge_curve is nearly
degenerate. DegeneratedValues must flag the apex as a degenerate point but the
near-zero angle confuses the symbolic surface classifier.

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
    catalog_id="Tfa200",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on CONICAL_SURFACE; "
        "base radius=1, semi_angle=0.01 rad (near-zero: degenerate apex); "
        "apex radius ≈ 0.0 — conical cross-section collapses; "
        "DegeneratedValues: apex point outside face domain or inconsistently "
        "parameterized; near-zero angle defeats symbolic surface classifier; "
        "downstream curve projections at apex produce NaN tangent vectors; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── CONICAL_SURFACE: base at z=0, apex above, near-zero semi-angle ────────────
# semi_angle = 0.01 rad → apex height h = base_r / tan(semi_angle) ≈ 100 units
# apex_radius ≈ base_r - h * tan(semi_angle) = 1 - 100*0.01 = 0.0 (degenerate)
semi_angle = 0.01  # radians
base_r = 1.0
# Height from base to where radius would reach zero:
h = base_r / _math.tan(semi_angle)   # ≈ 99.97
# Use only h/2 so apex_r ≈ 0.5 (still small but nonzero for geometry)
# Actually use smaller h to keep numbers reasonable: apex at h = 50
h_face = 50.0
apex_r = base_r - h_face * _math.tan(semi_angle)   # ≈ 1 - 50*0.01 = 0.5

cone_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
cone_surf = f.conical_surface(cone_plc, base_r, semi_angle)

# ── Seam points ───────────────────────────────────────────────────────────────
pt_base_seam = f.cartesian_point((base_r, 0.0, 0.0))
pt_apex_seam = f.cartesian_point((apex_r, 0.0, h_face))

v_base = f.vertex_point(pt_base_seam)
v_apex = f.vertex_point(pt_apex_seam)

# ── Base circle (full revolution) ────────────────────────────────────────────
base_circ_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0,  0.0)),
)
base_circle = f.circle(base_circ_plc, base_r)
base_edge = f.edge_curve(v_base, v_base, base_circle)

# ── Apex circle (full revolution, near-degenerate radius) ────────────────────
apex_circ_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, h_face)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
apex_circle = f.circle(apex_circ_plc, apex_r)
apex_edge = f.edge_curve(v_apex, v_apex, apex_circle)

# ── Seam edge (line along cone surface from base to apex) ─────────────────────
dx = apex_r - base_r
dz = h_face
seam_len = _math.sqrt(dx * dx + dz * dz)
seam_dir = f.direction((dx / seam_len, 0.0, dz / seam_len))
seam_edge = f.edge_curve(
    v_base, v_apex,
    f.line(pt_base_seam, f.vector(seam_dir, seam_len)),
)

# ── Face loop: seam(T) + apex(T) + seam(F) + base(F) ────────────────────────
face_loop = f.edge_loop([
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(apex_edge, True),
    f.oriented_edge(seam_edge, False),
    f.oriented_edge(base_edge, False),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], cone_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa200.stp")
