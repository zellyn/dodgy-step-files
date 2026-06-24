"""Me591 — holeFilling_TriangulateHole_angle_computation_failure: degenerate collinear boundary cycle; no valid triangulation vertex found (Branch 2).

MeshFix `holeFilling::TriangulateHole@L157` Branch 2 (*ANGLE_COMPUTATION_FAILURE*) @ line 183:
  'gang == DBL_MAX' → log warning; unmark vertices; return 0.
  TriangulateHole iterates the boundary cycle looking for the vertex whose
  opposite angle is minimum (minimum-weight triangulation). When all candidates
  produce angle == DBL_MAX (i.e., all are rejected by the convexity / angle
  constraint), the best-angle pointer is never set and gang remains DBL_MAX
  → Branch 2 fires.

Defect pattern: a nearly degenerate boundary cycle of 4 nearly collinear
  vertices around a paper-thin hole. The triangulation heuristic measures
  the angle at each candidate vertex; when all candidate angles violate the
  allowable range (e.g., reflex or nearly 180°), every candidate returns
  DBL_MAX and no vertex is selected → Branch 2.

Geometry: 4 triangles arranged around a thin slit hole.
  Outer ring: v0=(0,0,0), v1=(4,0,0), v2=(4,0.01,0), v3=(0,0.01,0) — nearly flat.
  Two bridging triangles (top/bottom pairs) create a paper-thin quadrilateral hole.
  The boundary of the hole is the inner square loop; all 4 candidate
  vertices sit at nearly 180° — angle computation returns DBL_MAX for each.

  Mesh: 6 vertices, 4 triangles, thin rectangular hole.
  v4=(1,0,0), v5=(3,0,0) — additional points on the bottom edge.
  Two upper triangles: t0=(v0,v4,v3), t1=(v4,v5,v3) — degenerate thin strip.
  Two lower triangles: t2=(v4,v1,v5), t3=(v0,v3,v4) reused.

We use a minimal 3-triangle strip with a single open boundary edge:
  v0=(0,0,0), v1=(4,0,0), v2=(4,0.005,0), v3=(0,0.005,0) — near-collinear quad hole.
  t0=(v0,v1,v2): bottom-right, t1=(v0,v2,v3): upper-left
  Open boundary: v0-v1 (bottom), v1-v2 (right), v2-v3 (top), v3-v0 (left)
  — all 4 boundary vertices are near-collinear; angle computation gives DBL_MAX.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me591",
    title="holeFilling_TriangulateHole_angle_computation_failure: near-collinear boundary cycle; all candidate angles == DBL_MAX; gang check fires (Branch 2)",
    defect_class="hole_in_hull",
)

# Near-collinear quad: the hole boundary is a paper-thin rectangle.
# Height 0.005 vs width 4 — extreme aspect ratio forces all candidate
# interior angles near 180° — none pass the minimum-angle triangulation test.
v0 = m.vertex(0.0, 0.000, 0.0)   # 0: bottom-left
v1 = m.vertex(4.0, 0.000, 0.0)   # 1: bottom-right
v2 = m.vertex(4.0, 0.005, 0.0)   # 2: top-right (extremely close to v1)
v3 = m.vertex(0.0, 0.005, 0.0)   # 3: top-left (extremely close to v0)

# Two triangles covering the flat rectangle — shared diagonal (v0,v2).
t0 = m.triangle(v0, v1, v2)  # 0: lower-right
t1 = m.triangle(v0, v2, v3)  # 1: upper-left

# Shared interior diagonal edge.
m.assert_edge_shared(v0, v2, 2)

# Boundary edges — 4 outer edges, each incident on 1 triangle.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Boundary cycle: near-collinear quad — all candidate angles ≈ 180°.
m.assert_hole_boundary([v0, v1, v2, v3])

# Degenerate aspect ratio: top edge much shorter than side in z-plane terms.
# v2-v3 distance ≈ 4.0 (width), v0-v3 distance ≈ 0.005 (height).
m.assert_vertex_pair_distance_lt(v0, v3, 0.01)
m.assert_vertex_pair_distance_lt(v1, v2, 0.01)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
