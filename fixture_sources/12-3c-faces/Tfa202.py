"""Tfa202 — CheckTwisted normal inversion on elementary

Cylindrical surface with reversed edge orientation (F/T/T/F pattern) inducing
normal inversion. Tests scalar product < 0 detection (twist angle > 90 degrees)
on elementary surface type.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a CYLINDRICAL_SURFACE. The
face boundary edges are given in the F/T/T/F oriented-edge pattern (first and
last oriented False, middle two True) which inverts the face normal relative to
the cylinder outward direction. The OCCT CheckTwisted at line 1015 evaluates
the scalar product between the surface normal and the oriented face normal; a
negative product (twist angle > 90°) triggers the "twisted face" branch. The
defect is the inconsistent edge orientation pattern, not the surface geometry.

Byte assertions:
  - contains(b'CYLINDRICAL_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa202",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on CYLINDRICAL_SURFACE; "
        "radius=1, height=1; "
        "edge loop uses F/T/T/F oriented-edge pattern: "
        "  seam F + top T + seam T + bottom F (inverted from canonical T/T/F/F); "
        "inverted loop orientation induces face normal pointing inward; "
        "CheckTwisted: scalar product(surface_normal, face_normal) < 0; "
        "twist angle > 90° triggers reorientation branch at line 1015; "
        "elementary surface type (cylinder) — no B-spline evaluation needed; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── CYLINDRICAL_SURFACE: radius=1, axis +Z ────────────────────────────────────
r = 1.0
h = 1.0

cyl_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
cyl_surf = f.cylindrical_surface(cyl_plc, r)

# ── Seam points ───────────────────────────────────────────────────────────────
pt_bot = f.cartesian_point((r, 0.0, 0.0))
pt_top = f.cartesian_point((r, 0.0, h))

v_bot = f.vertex_point(pt_bot)
v_top = f.vertex_point(pt_top)

# ── Seam edge (vertical line at u=0): v_bot → v_top ──────────────────────────
seam_edge = f.edge_curve(
    v_bot, v_top,
    f.line(pt_bot, f.vector(f.direction((0.0, 0.0, 1.0)), h)),
)

# ── Bottom circle (full revolution) ──────────────────────────────────────────
bot_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0,  0.0)),
)
bot_circle = f.circle(bot_plc, r)
bot_edge = f.edge_curve(v_bot, v_bot, bot_circle)

# ── Top circle (full revolution) ──────────────────────────────────────────────
top_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, h)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
top_circle = f.circle(top_plc, r)
top_edge = f.edge_curve(v_top, v_top, top_circle)

# ── Face loop: F/T/T/F pattern (defect: inverted orientation) ─────────────────
# Canonical outward cylinder: seam(T) + top(T) + seam(F) + bottom(F)
# Defect: seam(F) + top(T) + seam(T) + bottom(F)  → normal inverted inward
face_loop = f.edge_loop([
    f.oriented_edge(seam_edge, False),   # F — defect
    f.oriented_edge(top_edge,  True),
    f.oriented_edge(seam_edge, True),    # T — defect (wrong sense)
    f.oriented_edge(bot_edge,  False),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], cyl_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa202.stp")
