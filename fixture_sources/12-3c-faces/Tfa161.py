"""Tfa161 — ShapeFix_Face.FixOrientation single-loop-face.

Catalog claim: Face with exactly one loop (outer boundary only).
FixOrientation's containment-check logic assumes multiple wires exist for
inner-bound detection; single-wire case short-circuits when comparing against
non-existent inner wires, failing to validate self-orientation.
Triggers via Tfa161.stp (AUTOMOTIVE_DESIGN schema, PLANE surface, rectangular loop).

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE: a simple rectangle (4×3) on a
PLANE surface with a single FACE_OUTER_BOUND and no inner bounds.
FixOrientation's single-wire short-circuit path IS traversed.
Defect IS on live face traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa161",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on PLANE (4.0×3.0 rectangle); "
        "ONE FACE_OUTER_BOUND only — no inner bounds; "
        "FixOrientation single-loop short-circuit: containment-check skips "
        "inner-wire comparison because no inner wires exist; "
        "self-orientation validation fails to execute; "
        "defect IS on live OPEN_SHELL traversal path; "
        "no orphaned entities"
    ),
)

# ── PLANE surface at origin, normal +Z ────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
plane   = f.plane(f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir))

# ── Outer rectangle: 4.0 × 3.0 at (0,0)−(4,3) ────────────────────────────────
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((4.0, 0.0, 0.0))
p2 = f.cartesian_point((4.0, 3.0, 0.0))
p3 = f.cartesian_point((0.0, 3.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

ec_b = f.edge_curve(v0, v1, f.line(p0, f.vector(f.direction((1.0,  0.0, 0.0)), 4.0)))
ec_r = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction((0.0,  1.0, 0.0)), 3.0)))
ec_t = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 4.0)))
ec_l = f.edge_curve(v3, v0, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 3.0)))

outer_loop = f.edge_loop([
    f.oriented_edge(ec_b, True),
    f.oriented_edge(ec_r, True),
    f.oriented_edge(ec_t, True),
    f.oriented_edge(ec_l, True),
])

# ── Single ADVANCED_FACE: outer bound only — the FixOrientation trigger ────────
face = f.advanced_face([f.face_outer_bound(outer_loop)], plane)

# ── OPEN_SHELL → SBSM → product chain ─────────────────────────────────────────
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa161.stp")
