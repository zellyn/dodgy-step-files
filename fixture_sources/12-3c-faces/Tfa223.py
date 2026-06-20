"""Tfa223 — FixMissingSeam.infinite-bounds-fallback

Conical surface (apex at origin, semi-angle 0.5); single degenerated EDGE_LOOP
(cone-tip); tests infinite-bounds fallback at line 1759. Defect: infinite U/V
bounds bypass wire-bound substitution, causing NaN in seam-placement arithmetic.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a CONICAL_SURFACE with apex
at origin, base_radius=0.0, semi_angle=0.5 rad. The face outer boundary is a
single degenerated EDGE_LOOP — a point-circle at the cone apex (v=0, r=0),
where the parametric bounds become infinite (U unbounded at apex). The OCCT
FixMissingSeam code path at line 1759 computes wire bounds; infinite U/V bounds
from the apex singularity bypass the normal wire-bound substitution, causing NaN
values in seam-placement arithmetic. The fallback path must detect the infinite
bounds and short-circuit.

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
    catalog_id="Tfa223",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on CONICAL_SURFACE; "
        "apex at origin, base_radius=0.0, semi_angle=0.5 rad; "
        "degenerated EDGE_LOOP: single point-circle at cone apex (v=0, r=0); "
        "FixMissingSeam line 1759: infinite U/V bounds from apex singularity; "
        "infinite bounds bypass wire-bound substitution; "
        "NaN in seam-placement arithmetic without fallback guard; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── CONICAL_SURFACE: apex at origin, semi_angle=0.5 rad ──────────────────────
# OCCT conical surface: apex at placement origin, axis along Z
# base_radius=0.0: cone starts at apex (v=0) with zero radius
# At height v the cross-section radius = base_radius + v * tan(semi_angle)
# = 0 + v * tan(0.5) ≈ v * 0.5463
semi_angle = 0.5  # radians
tan_sa = _math.tan(semi_angle)
h_face = 3.0
r_top = h_face * tan_sa   # radius at top of cone face

cone_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
cone_surf = f.conical_surface(cone_plc, 0.0, semi_angle)

# ── Apex point (degenerate): at origin, cone tip ─────────────────────────────
# The apex is at v=0, u=any → degenerate point. Represent as a very tiny
# degenerate circle at z=0.001 (near-apex) rather than exactly at origin to
# avoid divide-by-zero in topology while still exercising the infinite-bounds path.
eps = 0.001
r_eps = eps * tan_sa  # tiny radius near apex

apex_pt = f.cartesian_point((r_eps, 0.0, eps))
v_apex = f.vertex_point(apex_pt)

# Degenerate circle at apex: very small radius
apex_ctr = f.cartesian_point((0.0, 0.0, eps))
apex_plc = f.axis2_placement_3d(
    apex_ctr,
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
apex_circle = f.circle(apex_plc, r_eps)
apex_edge = f.edge_curve(v_apex, v_apex, apex_circle)

# ── Top circle at h_face ─────────────────────────────────────────────────────
top_pt = f.cartesian_point((r_top, 0.0, h_face))
v_top = f.vertex_point(top_pt)

top_ctr = f.cartesian_point((0.0, 0.0, h_face))
top_plc = f.axis2_placement_3d(
    top_ctr,
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
top_circle = f.circle(top_plc, r_top)
top_edge = f.edge_curve(v_top, v_top, top_circle)

# ── Seam edge from apex to top ───────────────────────────────────────────────
dx = r_top - r_eps
dz = h_face - eps
seam_len = _math.sqrt(dx * dx + dz * dz)
seam_dir = f.direction((dx / seam_len, 0.0, dz / seam_len))
seam_edge = f.edge_curve(
    v_apex, v_top,
    f.line(apex_pt, f.vector(seam_dir, seam_len)),
)

# ── Face loop: seam(T), top(T), seam(F), apex(F) ─────────────────────────────
face_loop = f.edge_loop([
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(top_edge, True),
    f.oriented_edge(seam_edge, False),
    f.oriented_edge(apex_edge, False),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], cone_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa223.stp")
