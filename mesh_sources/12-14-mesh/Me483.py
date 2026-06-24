"""Me483 — removeTriangles null_edge_e3: triangle with zero-length third edge (e3 nulled).

Basic_TMesh.removeTriangles branch 4: null_edge_e3 —
  `|| t->e3 == NULL`

In the MeshFix half-edge structure e3 is the pointer to the closing edge of
the triangle (v2→v0). When that edge is detected as degenerate and severed
upstream, e3 becomes NULL and removeTriangles removes the triangle.

In a triangle-list mesh the representable equivalent is a triangle whose e3
edge (v2→v0) is zero-length: vertex-2 and vertex-0 are the same vertex, making
the closing edge a degenerate self-loop.

Fixture: t0 = (v0, v1, v0) — the edge from v0 (corner 2) back to v0 (corner 0)
is zero-length, representing the e3 == NULL condition. t1 is healthy.

Edge layout (triangle vertex ordering for degenerate t0):
  e1 = corner-0 → corner-1 = v0 → v1  (healthy length)
  e2 = corner-1 → corner-2 = v1 → v0  (healthy length, same as e1 reversed)
  e3 = corner-2 → corner-0 = v0 → v0  (zero-length — this is Branch 4)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me483",
             title="removeTriangles null_edge_e3: triangle [v0,v1,v0] has zero-length e3 edge (v0→v0), e3-NULL precondition (Branch 4)",
             defect_class="degenerate_triangle")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

# Healthy triangle.
t0 = m.triangle(v0, v1, v2)    # 0 — valid, area>0

# Degenerate triangle: e3 = edge from corner-2 to corner-0 = (v0, v0).
# Corner indices: [v0, v1, v0] — corner-2 and corner-0 are both v0.
# Zero-length e3 is the precondition for Branch 4 (t->e3 == NULL).
t1 = m.triangle(v0, v1, v0)    # 1 — degenerate; e3=(v0,v0) is zero-length

# t1 is exactly degenerate (area = 0).
m.assert_triangle_area_lt(1, 1e-12)

# The self-loop edge (v0,v0) appears only in t1.
m.assert_edge_shared(v0, v0, 1)

# v0 to v0 distance is zero — coincident endpoints of the e3 self-loop.
m.assert_vertex_pair_distance_lt(v0, v0, 1e-12)
