"""Me200 — zip_vertex_edge_list: vertex has incident boundary edges eligible for zip.

MeshFix `Vertex.zip` Branch 1 (*vertex_edge_list*) @ line 563:
  'VE* ve = VE()'
  zip() begins by collecting the circular list of edges incident on the vertex.
  Branch 1 covers the case where the vertex actually has incident edges (non-empty
  VE list), so the algorithm can proceed.

Defect pattern: a boundary vertex v0 sits at the junction of two open triangle
fans (an open strip with two boundary edges meeting at v0). zip() finds v0's
incident edge list non-empty and can enumerate the boundary edges be1 and be2.
Without zip, the two boundary edges remain unmerged; the mesh has an open seam
at v0.

Geometry: two triangles sharing vertex v0, each with one boundary edge incident
on v0. v0 lies at the junction of the open boundary.
  v0=(0,0,0), v1=(1,0,0), v2=(-1,0,0), v3=(0,1,0)
  t0 = (v0, v1, v3) — boundary edge (v0,v1) on this triangle
  t1 = (v0, v3, v2) — boundary edge (v0,v2) on this triangle

Both boundary edges are incident on v0 — zip() VE() call finds this list non-empty.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me200",
             title="zip_vertex_edge_list: vertex v0 has non-empty incident-edge list enabling zip boundary walk",
             defect_class="zip_vertex_edge_list")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — junction vertex; incident on two boundary edges
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(-1.0, 0.0, 0.0)  # 2
v3 = m.vertex(0.0, 1.0, 0.0)   # 3 — shared interior apex

t0 = m.triangle(v0, v1, v3)    # 0
t1 = m.triangle(v0, v3, v2)    # 1

# Shared interior edge (v0,v3) — confirms v0 is an interior shared vertex
m.assert_edge_shared(v0, v3, 2)

# Both boundary edges incident on v0 — VE() list is non-empty
m.assert_edge_shared(v0, v1, 1)  # boundary on t0; be1 candidate
m.assert_edge_shared(v0, v2, 1)  # boundary on t1; be2 candidate

# Remaining boundary edges
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)
