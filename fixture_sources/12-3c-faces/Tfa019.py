"""Tfa019 — Adjacent ADVANCED_FACEs with distinct VERTEX_POINT/EDGE_CURVE
for the same shared boundary (FaceConnect: vertices not shared).

Catalog claim: Two ADVANCED_FACEs that touch along a physical shared boundary
use distinct VERTEX_POINT instances on each side and distinct EDGE_CURVE
instances for what should be one shared edge — each owns its own vertex /
edge copy. Common signature: an OPEN_SHELL of two coplanar faces meeting at
x=10, where face A uses vertices (#30, #31) and edge #71 along that border
while face B uses vertices (#34, #37) and edge #77 — duplicate vertices at the
seam needing connect / sew. Distance-only checks pass but the shell has
zero-tolerance topological cracks.

Mechanism: OPEN_SHELL with TWO ADVANCED_FACEs on PLANE:
  face[0] — left 10×10 square (x:0–10, y:0–10); right edge uses vertices
    v1_a=(10,0,0) and v2_a=(10,10,0) + EDGE_CURVE ec_shared_a
  face[1] — right 10×10 square (x:10–20, y:0–10); left edge uses
    DISTINCT vertices v1_b=(10,0,0) and v2_b=(10,10,0) + DISTINCT
    EDGE_CURVE ec_shared_b (geometrically identical but separate entities)
  The shared boundary at x=10 has four VERTEX_POINT entities
  instead of two, and two EDGE_CURVE entities instead of one — topology crack.

Tier-3 assertions:
  n_edges_total >= 8
  face[0].surface_type == "plane"
  face[1].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa019",
    defect=(
        "OPEN_SHELL: two adjacent 10×10 coplanar ADVANCED_FACEs meeting at x=10; "
        "face[0] uses vertices v1_a=(10,0,0), v2_a=(10,10,0) and ec_shared_a at the boundary; "
        "face[1] uses DISTINCT vertices v1_b=(10,0,0), v2_b=(10,10,0) and ec_shared_b — "
        "geometrically identical but topologically separate; "
        "four VERTEX_POINTs at x=10 instead of two, two EDGE_CURVEs instead of one; "
        "topology crack: distance-only checks pass but shell has no shared edge; "
        "FaceConnect/ShapeFix_Shell must merge coincident vertices/edges within tolerance; "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# Shared PLANE for both faces
pl_orig  = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir  = f.direction((0.0, 0.0, 1.0))
pl_xdir  = f.direction((1.0, 0.0, 0.0))
pl_plc   = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane    = f.plane(pl_plc)

# ── face[0]: left square vertices/edges ─────────────────────────────────────
p0_a = f.cartesian_point(( 0.0,  0.0, 0.0))  # bottom-left
p1_a = f.cartesian_point((10.0,  0.0, 0.0))  # bottom-right (boundary side A)
p2_a = f.cartesian_point((10.0, 10.0, 0.0))  # top-right (boundary side A)
p3_a = f.cartesian_point(( 0.0, 10.0, 0.0))  # top-left

v0_a = f.vertex_point(p0_a)
v1_a = f.vertex_point(p1_a)   # at x=10, y=0 — side A copy
v2_a = f.vertex_point(p2_a)   # at x=10, y=10 — side A copy
v3_a = f.vertex_point(p3_a)

ec_a_bot    = f.edge_curve(v0_a, v1_a, f.line(p0_a, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
ec_shared_a = f.edge_curve(v1_a, v2_a, f.line(p1_a, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec_a_top    = f.edge_curve(v2_a, v3_a, f.line(p2_a, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
ec_a_left   = f.edge_curve(v3_a, v0_a, f.line(p3_a, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

loop_a = f.edge_loop([
    f.oriented_edge(ec_a_bot,    True),
    f.oriented_edge(ec_shared_a, True),
    f.oriented_edge(ec_a_top,    True),
    f.oriented_edge(ec_a_left,   True),
])
fob_a  = f.face_outer_bound(loop_a)
face_a = f.advanced_face([fob_a], plane)

# ── face[1]: right square with DUPLICATE boundary vertices/edges ─────────────
# Geometrically coincident with v1_a / v2_a / ec_shared_a but distinct entities
p1_b = f.cartesian_point((10.0,  0.0, 0.0))  # same coords as p1_a — duplicate
p2_b = f.cartesian_point((10.0, 10.0, 0.0))  # same coords as p2_a — duplicate
p4_b = f.cartesian_point((20.0,  0.0, 0.0))
p5_b = f.cartesian_point((20.0, 10.0, 0.0))

v1_b = f.vertex_point(p1_b)   # at x=10, y=0 — side B copy (DUPLICATE of v1_a)
v2_b = f.vertex_point(p2_b)   # at x=10, y=10 — side B copy (DUPLICATE of v2_a)
v4_b = f.vertex_point(p4_b)
v5_b = f.vertex_point(p5_b)

# DUPLICATE shared edge — same geometry as ec_shared_a but different entity
ec_shared_b = f.edge_curve(v1_b, v2_b, f.line(p1_b, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec_b_bot    = f.edge_curve(v1_b, v4_b, f.line(p1_b, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
ec_b_right  = f.edge_curve(v4_b, v5_b, f.line(p4_b, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec_b_top    = f.edge_curve(v5_b, v2_b, f.line(p5_b, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))

loop_b = f.edge_loop([
    f.oriented_edge(ec_shared_b, False),  # (10,10)→(10,0) on face[1]'s left side
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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa019.stp")
