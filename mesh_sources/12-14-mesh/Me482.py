"""Me482 — removeTriangles null_edge_e2: triangle with zero-length second edge (e2 nulled).

Basic_TMesh.removeTriangles branch 3: null_edge_e2 —
  `|| t->e2 == NULL ||`

In the MeshFix half-edge structure e2 is the pointer to the edge connecting
the second and third vertex of the triangle (v1→v2). When that edge is
detected as degenerate and severed upstream, e2 becomes NULL and removeTriangles
removes the triangle.

In a triangle-list mesh the representable equivalent is a triangle whose e2
edge (v1→v2) is zero-length: vertex-1 and vertex-2 are the same vertex, making
the edge from corner-1 to corner-2 a degenerate self-loop.

Fixture: t0 = (v0, v1, v1) — the edge from v1 to v1 (corner 1 → corner 2)
is zero-length, representing the e2 == NULL condition. t1 is healthy.

Edge layout (triangle vertex ordering):
  e1 = corner-0 → corner-1 = v0 → v1  (healthy)
  e2 = corner-1 → corner-2 = v1 → v1  (zero-length — this is Branch 3)
  e3 = corner-2 → corner-0 = v1 → v0  (degenerate by transitivity)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me482",
             title="removeTriangles null_edge_e2: triangle [v0,v1,v1] has zero-length e2 edge (v1→v1), e2-NULL precondition (Branch 3)",
             defect_class="degenerate_triangle")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

# Healthy triangle.
t0 = m.triangle(v0, v1, v2)    # 0 — valid, area>0

# Degenerate triangle: e2 = edge from corner-1 to corner-2 = (v1, v1).
# Zero-length e2 is the precondition for Branch 3 (t->e2 == NULL).
t1 = m.triangle(v0, v1, v1)    # 1 — degenerate; e2=(v1,v1) is zero-length

# t1 is exactly degenerate.
m.assert_triangle_area_lt(1, 1e-12)

# The self-loop edge (v1,v1) appears only in t1.
m.assert_edge_shared(v1, v1, 1)

# v1 to v1 distance is zero — coincident endpoints of the e2 self-loop.
m.assert_vertex_pair_distance_lt(v1, v1, 1e-12)
