"""Me203 — zip_edge_not_boundary: vertex has non-boundary edge at head or tail → zip returns 0.

MeshFix `Vertex.zip` Branch 4 (*edge_not_boundary*) @ line 567:
  'if (!be1->isOnBoundary() || !be2->isOnBoundary()) return 0'
  After collecting be1 and be2, zip verifies both are boundary edges. If either is
  not on the boundary (i.e. interior, shared by 2 triangles), zip aborts with 0.
  Branch 4 covers an interior vertex where the "boundary" edges fail the test.

Defect pattern: vertex v0 is fully enclosed (all incident edges are interior). When
zip() is called on v0, neither be1 nor be2 is a boundary edge → zip returns 0 without
modifying the mesh. This represents a non-boundary vertex where zip is not applicable.

Geometry: a closed four-triangle fan around v0 — all edges from v0 are interior.
  v0=(0,0,0), v1=(1,0,0), v2=(0,1,0), v3=(-1,0,0), v4=(0,-1,0)
  t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4), t3=(v0,v4,v1)

All edges (v0,v1), (v0,v2), (v0,v3), (v0,v4) are interior (n=2). zip's boundary
check at Branch 4 fails and returns 0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me203",
             title="zip_edge_not_boundary: closed fan around v0 means no boundary edges at head/tail → zip aborts",
             defect_class="zip_edge_not_boundary")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — enclosed interior vertex
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3
v4 = m.vertex(0.0, -1.0, 0.0)  # 4

t0 = m.triangle(v0, v1, v2)    # 0
t1 = m.triangle(v0, v2, v3)    # 1
t2 = m.triangle(v0, v3, v4)    # 2
t3 = m.triangle(v0, v4, v1)    # 3

# All edges from v0 are interior (shared by 2 triangles each)
# zip Branch 4: neither be1 nor be2 is on boundary → return 0
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v0, v4, 2)

# Outer boundary ring (each outer edge is boundary)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v1, 1)
