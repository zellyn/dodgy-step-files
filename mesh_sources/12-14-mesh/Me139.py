"""Me139 — removeIfRedundant_collapse_failure: the edge collapse operation returns
NULL, indicating the collapse is topologically invalid.

MeshFix `Vertex.removeIfRedundant` Branch 10 (*collapse_failure*) @ line 394:
  'if ((result = e->collapseOnV1()) == NULL) return false'
  After all prior checks pass and a collapse edge 'e' is selected, the algorithm
  attempts the actual collapse via e->collapseOnV1(). If the collapse fails
  (returns NULL — e.g. because it would create a non-manifold configuration or
  violate link condition), removeIfRedundant returns false at Branch 10.

Geometric signature: vertex v2 is a Flat interior vertex on a closed strip (all
its incident edges are interior). The collapse of edge (v0,v2) would merge v2
into v0, but doing so would create a degenerate triangle (the triangle (v0,v2,v1)
would become (v0,v0,v1) with zero area). This mimics the link-condition failure
that causes collapseOnV1() to return NULL.

Geometry (z=0): A closed fan of 4 triangles around v2 on a flat disc. Collapsing
v2 onto v0 would merge two triangles into coincident degenerate triangles.
  v0=(0,0,0), v1=(1,1,0), v2=(0,2,0), v3=(-1,1,0) [outer ring]
  v4=(0,0.8,0)  ← inner subject vertex (Flat, surrounded by closed fan)

  Fan around v4:
    t0 = (v0, v1, v4)
    t1 = (v1, v2, v4)
    t2 = (v2, v3, v4)
    t3 = (v3, v0, v4)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me139",
             title="removeIfRedundant_collapse_failure: edge collapse returns NULL due to degenerate result, removal blocked",
             defect_class="redundant_vertex_removal_collapse_failure")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — outer ring
v1 = m.vertex(1.0, 1.0, 0.0)   # 1 — outer ring
v2 = m.vertex(0.0, 2.0, 0.0)   # 2 — outer ring
v3 = m.vertex(-1.0, 1.0, 0.0)  # 3 — outer ring
v4 = m.vertex(0.0, 0.8, 0.0)   # 4 — interior Flat subject vertex

t0 = m.triangle(v0, v1, v4)    # 0
t1 = m.triangle(v1, v2, v4)    # 1
t2 = m.triangle(v2, v3, v4)    # 2
t3 = m.triangle(v3, v0, v4)    # 3

# All four fan edges at v4 are interior (closed fan — collapse would fail
# the link condition since v0 is already adjacent to v1, v2, and v3).
m.assert_edge_shared(v0, v4, 2)   # shared by t0 and t3
m.assert_edge_shared(v1, v4, 2)   # shared by t0 and t1
m.assert_edge_shared(v2, v4, 2)   # shared by t1 and t2
m.assert_edge_shared(v3, v4, 2)   # shared by t2 and t3

# Outer ring edges are also interior (closed patch).
m.assert_edge_shared(v0, v1, 1)   # boundary: only t0
m.assert_edge_shared(v1, v2, 1)   # boundary: only t1
m.assert_edge_shared(v2, v3, 1)   # boundary: only t2
m.assert_edge_shared(v3, v0, 1)   # boundary: only t3
