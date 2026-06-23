"""Me202 — zip_boundary_edge_last: tail edge in circular list is boundary → selected as be2.

MeshFix `Vertex.zip` Branch 3 (*boundary_edge_last*) @ line 565:
  'be2 = ve->tail()->data'
  After be1 is found at the head, zip scans the circular list and takes the tail edge
  as be2, provided it is also a boundary edge. Branch 3 covers this tail selection.

Defect pattern: a boundary vertex v0 with three incident edges arranged so that the
first (head) incident edge is boundary (be1) and the last (tail) incident edge is also
boundary (be2). The middle edges are interior. zip identifies both boundary endpoints
of the open fan.

Geometry: three-triangle fan at v0; outer two edges are boundary, middle edge is interior.
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(0,2,0)
  t0 = (v0, v1, v2)  — (v0,v1) boundary [be1/head], (v0,v2) interior
  t1 = (v0, v2, v3)  — (v0,v2) interior, (v0,v3) boundary [be2/tail]

Oracle confirms (v0,v1) and (v0,v3) are boundary (n=1), (v0,v2) is interior (n=2).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me202",
             title="zip_boundary_edge_last: tail of VE circular list for v0 is boundary edge → assigned as be2",
             defect_class="zip_boundary_edge_last")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — junction vertex
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — head-edge endpoint (be1)
v2 = m.vertex(1.0, 1.0, 0.0)   # 2 — middle vertex (interior edge to v0)
v3 = m.vertex(0.0, 2.0, 0.0)   # 3 — tail-edge endpoint (be2)

t0 = m.triangle(v0, v1, v2)    # 0
t1 = m.triangle(v0, v2, v3)    # 1

# Interior shared edge — confirms v0 has interior edges between the two boundary ones
m.assert_edge_shared(v0, v2, 2)

# Head boundary edge (be1)
m.assert_edge_shared(v0, v1, 1)

# Tail boundary edge (be2) — Branch 3 assigns this as be2
m.assert_edge_shared(v0, v3, 1)

# Remaining boundary edges
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
