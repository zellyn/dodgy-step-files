"""Me481 — removeTriangles null_edge_e1: triangle with zero-length first edge (e1 nulled).

Basic_TMesh.removeTriangles branch 2: null_edge_e1 —
  `if (t->e1 == NULL || t->e2 == NULL || t->e3 == NULL)`

In the MeshFix half-edge structure, each triangle holds three edge pointers
(e1, e2, e3) corresponding to edges v0→v1, v1→v2, v2→v0. When an upstream
cleanup step detects a completely degenerate edge and severs it, e1 is set to
NULL. The removeTriangles loop then detects this NULL and removes the triangle.

In a triangle-list mesh the nearest representable equivalent is a triangle
whose e1-edge (v0→v1) is zero-length: both endpoints are the same vertex, so
the edge has no length and would be nulled out by any edge-validity filter.

Fixture: t0 = (v0, v0, v2) — the edge from v0 to v0 is a zero-length
self-loop, representing the e1 == NULL condition. t1 is a healthy companion.

e1 maps to the edge from the first to the second vertex of the triangle
(index 0 → index 1). Here both are v0, so edge e1 is degenerate.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me481",
             title="removeTriangles null_edge_e1: triangle [v0,v0,v2] has zero-length e1 edge (v0→v0), e1-NULL precondition (Branch 2)",
             defect_class="degenerate_triangle")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

# Healthy triangle.
t0 = m.triangle(v0, v1, v2)    # 0 — valid, area>0

# Degenerate triangle: e1 = edge from corner-0 to corner-1 = (v0, v0).
# Zero-length e1 is the precondition for Branch 2 (t->e1 == NULL).
t1 = m.triangle(v0, v0, v2)    # 1 — degenerate; e1=(v0,v0) is zero-length

# t1 is exactly degenerate.
m.assert_triangle_area_lt(1, 1e-12)

# The self-loop edge (v0,v0) appears only in t1.
m.assert_edge_shared(v0, v0, 1)

# v0 to v0 distance is zero — coincident endpoints.
m.assert_vertex_pair_distance_lt(v0, v0, 1e-12)
