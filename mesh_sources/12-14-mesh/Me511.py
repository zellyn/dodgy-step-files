"""Me511 — Edge.swap branch 2: EDGE_TOPOLOGY_EXTRACTION.

MeshFix `Edge.swap` Branch 2 (*EDGE_TOPOLOGY_EXTRACTION*) @ line 150:
  'Edge *e1 = t1->nextEdge(this); Edge *e3 = t2->nextEdge(this);'
  — for any swappable interior edge, the algorithm extracts the next edges
  in t1 and t2 that follow the shared edge in each triangle's winding order.
  These extracted edges (e1 from t1, e3 from t2) will be swapped between
  the two triangles in the subsequent replacement step. Branch 2 fires for
  any interior edge with two incident triangles.

Defect pattern: a minimal 2-triangle quad (4 vertices, 5 edges) with one
  interior diagonal. The diagonal (v0,v2) is the swappable interior edge.
  Its next edge in t0 is e1=(v2,v1) and its next edge in t1 is e3=(v2,v3).
  Topology extraction fires immediately on entering swap for this edge.

Geometry (z=0):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(-0.5,0.5,0)
  t0=(v0,v1,v2) — left triangle; nextEdge(v0-v2) from v2 is the edge to v1
  t1=(v0,v2,v3) — right triangle; nextEdge(v0-v2) from v2 is the edge to v3

Interior diagonal (v0,v2) has n=2; all outer edges are boundary (n=1).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me511",
    title="Edge.swap EDGE_TOPOLOGY_EXTRACTION: interior diagonal (v0,v2) with two incident triangles; e1=nextEdge(t0) and e3=nextEdge(t1) extracted for cycle replacement (Branch 2)",
    defect_class="edge_swap_topology_extraction",
)

v0 = m.vertex(0.0,  0.0,  0.0)   # 0 — shared diagonal endpoint (bottom)
v1 = m.vertex(1.0,  0.0,  0.0)   # 1 — opposite vertex of t0
v2 = m.vertex(0.5,  1.0,  0.0)   # 2 — shared diagonal endpoint (top)
v3 = m.vertex(-0.5, 0.5,  0.0)   # 3 — opposite vertex of t1

# Two-triangle quad sharing diagonal (v0,v2).
t0 = m.triangle(v0, v1, v2)   # 0: left triangle
t1 = m.triangle(v0, v2, v3)   # 1: right triangle

# Shared interior diagonal — both incident triangles present → e1, e3 can be extracted.
m.assert_edge_shared(v0, v2, 2)

# Boundary edges — n=1 each.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
