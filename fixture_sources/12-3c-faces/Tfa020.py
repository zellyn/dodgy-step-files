"""Tfa020 — Sewing — free bounds on closed shell.

Catalog claim: A shell that should be closed has free (naked) edges; edges
incident to fewer than two faces. Either a face is missing (W009), or adjacent
face boundaries weren't sewn within tolerance.

Mechanism: OPEN_SHELL with TWO ADVANCED_FACEs on PLANE, adjacent but using
  DISTINCT EDGE_CURVE entities at the shared boundary (within 1e-5 mm
  distance but referencing different records). The shell is declared as
  OPEN_SHELL (it *should* be closed but isn't). Free edges appear at the
  seam between the two faces because they reference different EDGE_CURVE
  entities for what should be one shared edge.

  face[0] — left 10×10 square (x:0–10, y:0–10); right boundary uses
    ec_shared_a from v1_a=(10,0,0) to v2_a=(10,10,0)
  face[1] — right 10×10 square (x:10+1e-5, y:0–10); left boundary uses
    ec_shared_b from v1_b=(10.00001,0,0) to v2_b=(10.00001,10,0)
    — offset by 1e-5 mm (within sewing tolerance 1e-4 but different EDGE_CURVE)
  Free edges: ec_shared_a (face[0]'s right) and ec_shared_b (face[1]'s left)
  are both naked edges — each belongs to only one face.

Tier-3 assertions:
  n_edges_total >= 8
  face[0].surface_type == "plane"
  face[1].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa020",
    defect=(
        "OPEN_SHELL: two 10×10 coplanar ADVANCED_FACEs with free boundary edges; "
        "face[0] right edge at x=10 (ec_shared_a) and face[1] left edge at x=10.00001 "
        "(ec_shared_b, offset 1e-5 mm) are distinct EDGE_CURVEs — each belongs to only one face; "
        "free naked edges on what should be a closed shell; "
        "distance-gap is 1e-5 mm (within 1e-4 sewing tolerance) but topology has no shared edge; "
        "ShapeFix_Shell/ShapeUpgrade_ShellSewing must stitch free boundaries pairwise; "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# ── PLANE for both faces ──────────────────────────────────────────────────────
pl_orig  = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir  = f.direction((0.0, 0.0, 1.0))
pl_xdir  = f.direction((1.0, 0.0, 0.0))
pl_plc   = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane    = f.plane(pl_plc)

# ── face[0]: left 10×10 square (x:0–10) ──────────────────────────────────────
p0_a = f.cartesian_point(( 0.0,  0.0, 0.0))
p1_a = f.cartesian_point((10.0,  0.0, 0.0))   # right boundary — free edge end
p2_a = f.cartesian_point((10.0, 10.0, 0.0))   # right boundary — free edge end
p3_a = f.cartesian_point(( 0.0, 10.0, 0.0))

v0_a = f.vertex_point(p0_a)
v1_a = f.vertex_point(p1_a)
v2_a = f.vertex_point(p2_a)
v3_a = f.vertex_point(p3_a)

ec_a_bot    = f.edge_curve(v0_a, v1_a, f.line(p0_a, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
ec_shared_a = f.edge_curve(v1_a, v2_a, f.line(p1_a, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec_a_top    = f.edge_curve(v2_a, v3_a, f.line(p2_a, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
ec_a_left   = f.edge_curve(v3_a, v0_a, f.line(p3_a, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

loop_a = f.edge_loop([
    f.oriented_edge(ec_a_bot,    True),
    f.oriented_edge(ec_shared_a, True),   # FREE EDGE — naked boundary
    f.oriented_edge(ec_a_top,    True),
    f.oriented_edge(ec_a_left,   True),
])
fob_a  = f.face_outer_bound(loop_a)
face_a = f.advanced_face([fob_a], plane)

# ── face[1]: right 10×10 square offset 1e-5 mm ───────────────────────────────
# Left boundary at x=10.00001 — within sewing tolerance (1e-4) but distinct entity
gap = 1.0e-5
x1 = 10.0 + gap   # 10.00001

p1_b = f.cartesian_point((x1,        0.0, 0.0))   # left boundary — free edge (offset)
p2_b = f.cartesian_point((x1,       10.0, 0.0))   # left boundary — free edge (offset)
p4_b = f.cartesian_point((x1 + 10.0, 0.0, 0.0))  # right
p5_b = f.cartesian_point((x1 + 10.0,10.0, 0.0))  # right

v1_b = f.vertex_point(p1_b)
v2_b = f.vertex_point(p2_b)
v4_b = f.vertex_point(p4_b)
v5_b = f.vertex_point(p5_b)

ec_shared_b = f.edge_curve(v1_b, v2_b, f.line(p1_b, f.vector(f.direction((0.0, 1.0, 0.0)), 10.0)))
ec_b_bot    = f.edge_curve(v1_b, v4_b, f.line(p1_b, f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)))
ec_b_right  = f.edge_curve(v4_b, v5_b, f.line(p4_b, f.vector(f.direction((0.0, 1.0, 0.0)), 10.0)))
ec_b_top    = f.edge_curve(v5_b, v2_b, f.line(p5_b, f.vector(f.direction((-1.0,0.0, 0.0)), 10.0)))

loop_b = f.edge_loop([
    f.oriented_edge(ec_shared_b, False),  # FREE EDGE — naked boundary (reversed)
    f.oriented_edge(ec_b_bot,    True),
    f.oriented_edge(ec_b_right,  True),
    f.oriented_edge(ec_b_top,    True),
])
fob_b  = f.face_outer_bound(loop_b)
face_b = f.advanced_face([fob_b], plane)

# ── Wire both into OPEN_SHELL → SBSM → product chain ─────────────────────────
shell = f.open_shell([face_a, face_b])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa020.stp")
