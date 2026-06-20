"""Tfa023 — STEP file delivers disjoint faces with no shell wrapping (sewing required).

Catalog claim: A multi-face STEP file exports as a flat collection of disjoint
faces — no CLOSED_SHELL, no OPEN_SHELL, no MANIFOLD_SOLID_BREP — sometimes
wrapped only as a top-level SHELL_BASED_SURFACE_MODEL. The downstream consumer
needs to stitch the faces back into shells based on geometric coincidence at
boundaries.

Mechanism: SHELL_BASED_SURFACE_MODEL with two 1-face OPEN_SHELLs — each
ADVANCED_FACE is wrapped in its own single-face OPEN_SHELL with NO topological
connection between the two shells. The two faces are geometrically adjacent
(sharing a boundary at x=10) but live in separate un-stitched shells.

  shell[0] → face[0]: left 10×10 square (x:0–10, y:0–10)
  shell[1] → face[1]: right 10×10 square (x:10–20, y:0–10)
  Both faces share boundary geometry at x=10 but no shared EDGE_CURVE/
  VERTEX_POINT topology — unstitched seam.

The downstream healer (ShapeUpgrade_ShellSewing) must discover that shell[0]
and shell[1] are sewable, merge them into one shell, and report per-face
diagnostics for joined boundaries.

Tier-3 assertions:
  n_edges_total >= 8
  face[0].surface_type == "plane"
  face[1].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(15) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa023",
    defect=(
        "SHELL_BASED_SURFACE_MODEL with two separate OPEN_SHELLs — each 1 face; "
        "face[0] left 10×10 square (x:0–10) in shell[0]; "
        "face[1] right 10×10 square (x:10–20) in shell[1]; "
        "no shared EDGE_CURVE or VERTEX_POINT at x=10 — unstitched seam; "
        "no CLOSED_SHELL wrapping; faces are geometrically adjacent but topologically disjoint; "
        "ShapeUpgrade_ShellSewing must stitch shell[0]+shell[1] into one sewn shell; "
        "defect IS on live face traversal path: both shells are in the SBSM"
    ),
)

# Shared PLANE for both faces
pl_orig  = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir  = f.direction((0.0, 0.0, 1.0))
pl_xdir  = f.direction((1.0, 0.0, 0.0))
pl_plc   = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane    = f.plane(pl_plc)

# ── face[0]: left 10×10 square (x:0–10) ──────────────────────────────────────
p0_a = f.cartesian_point(( 0.0,  0.0, 0.0))
p1_a = f.cartesian_point((10.0,  0.0, 0.0))
p2_a = f.cartesian_point((10.0, 10.0, 0.0))
p3_a = f.cartesian_point(( 0.0, 10.0, 0.0))

v0_a = f.vertex_point(p0_a)
v1_a = f.vertex_point(p1_a)
v2_a = f.vertex_point(p2_a)
v3_a = f.vertex_point(p3_a)

ec_a_bot   = f.edge_curve(v0_a, v1_a, f.line(p0_a, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
ec_a_right = f.edge_curve(v1_a, v2_a, f.line(p1_a, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec_a_top   = f.edge_curve(v2_a, v3_a, f.line(p2_a, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
ec_a_left  = f.edge_curve(v3_a, v0_a, f.line(p3_a, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

loop_a = f.edge_loop([
    f.oriented_edge(ec_a_bot,   True),
    f.oriented_edge(ec_a_right, True),
    f.oriented_edge(ec_a_top,   True),
    f.oriented_edge(ec_a_left,  True),
])
fob_a  = f.face_outer_bound(loop_a)
face_a = f.advanced_face([fob_a], plane)

# ── face[1]: right 10×10 square (x:10–20) ────────────────────────────────────
# Geometrically adjacent at x=10 but NO shared topology with face[0]
p0_b = f.cartesian_point((10.0,  0.0, 0.0))  # same coords as p1_a — but distinct
p1_b = f.cartesian_point((20.0,  0.0, 0.0))
p2_b = f.cartesian_point((20.0, 10.0, 0.0))
p3_b = f.cartesian_point((10.0, 10.0, 0.0))  # same coords as p2_a — but distinct

v0_b = f.vertex_point(p0_b)
v1_b = f.vertex_point(p1_b)
v2_b = f.vertex_point(p2_b)
v3_b = f.vertex_point(p3_b)

ec_b_bot   = f.edge_curve(v0_b, v1_b, f.line(p0_b, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
ec_b_right = f.edge_curve(v1_b, v2_b, f.line(p1_b, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec_b_top   = f.edge_curve(v2_b, v3_b, f.line(p2_b, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
ec_b_left  = f.edge_curve(v3_b, v0_b, f.line(p3_b, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

loop_b = f.edge_loop([
    f.oriented_edge(ec_b_bot,   True),
    f.oriented_edge(ec_b_right, True),
    f.oriented_edge(ec_b_top,   True),
    f.oriented_edge(ec_b_left,  True),
])
fob_b  = f.face_outer_bound(loop_b)
face_b = f.advanced_face([fob_b], plane)

# ── Two separate OPEN_SHELLs — each with one face (the defect: no stitching) ─
shell_a = f.open_shell([face_a])   # un-stitched shell for face[0]
shell_b = f.open_shell([face_b])   # un-stitched shell for face[1]

# SHELL_BASED_SURFACE_MODEL aggregates both shells but does NOT stitch them —
# the sewing must be performed by the downstream healer.
sbsm = f.shell_based_surface_model([shell_a, shell_b])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa023.stp")
