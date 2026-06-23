"""Me201 — zip_boundary_edge_first: head edge in circular list is boundary → selected as be1.

MeshFix `Vertex.zip` Branch 2 (*boundary_edge_first*) @ line 564:
  'be1 = ve->head()->data'
  After collecting the VE list, zip walks it to find the two boundary edges. Branch 2
  covers the case where the *first* (head) edge in the circular list is a boundary edge,
  and it is assigned as be1.

Defect pattern: a boundary vertex v0 with its head edge (the first in the incident-edge
circular list) being a boundary edge. The mesh has an open seam: two boundary halfedges
meet at v0 and the zip operation needs to identify be1 as the head boundary edge.

Geometry: three-triangle open fan at v0 — first and last edges are boundary.
  v0=(0,0,0), v1=(1,0,0), v2=(0,1,0), v3=(-1,0,0)
  t0 = (v0, v1, v2)  — boundary edges (v0,v1) [head] and (v0,v2) shared
  t1 = (v0, v2, v3)  — boundary edges (v0,v2) shared and (v0,v3) [tail]
  The head edge in the VE list for v0 corresponds to (v0,v1): boundary → be1.

Oracle confirms (v0,v1) is a boundary edge (incident on exactly 1 triangle).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me201",
             title="zip_boundary_edge_first: head of VE circular list for v0 is boundary edge → assigned as be1",
             defect_class="zip_boundary_edge_first")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — junction vertex
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — head-edge neighbor (be1 endpoint)
v2 = m.vertex(0.0, 1.0, 0.0)   # 2 — middle vertex
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3 — tail-edge neighbor

t0 = m.triangle(v0, v1, v2)    # 0
t1 = m.triangle(v0, v2, v3)    # 1

# Interior shared edge
m.assert_edge_shared(v0, v2, 2)

# Head boundary edge (be1) — first in VE list for v0
m.assert_edge_shared(v0, v1, 1)

# Tail boundary edge (be2) — last in VE list for v0
m.assert_edge_shared(v0, v3, 1)

# Remaining boundary edges
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
