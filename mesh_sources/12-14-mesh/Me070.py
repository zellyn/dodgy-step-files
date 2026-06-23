"""Me070 — duplicate_singular_vertices: minimal bowtie vertex in the XY plane.

Catalog claim: vertex 0 is a non-manifold (singular) vertex whose link has 2
connected components. CGAL PMP.Polygon_soup_orienter.duplicate_singular_vertices
Branch 5 (*non_manifold_vertex*) fires when the link-CC count for a vertex
exceeds 1, marking it as needing duplication. The per-vertex incident-polygon
list (Branch 1, *incident_polygon_collection*) is built first, then the vertex
is iterated (Branch 2, *vertex_iteration*) and its link CC count computed
(Branch 4, *link_cc_count*).

Defect carrier: two triangles in the XY plane share only vertex 0 with no
shared edge. Upper fan (v0,v1,v2) and lower fan (v0,v3,v4) form two disjoint
link components at v0. Removing v0 leaves two completely disconnected patches.

Layout:
  v1=(1,1,0)  v2=(-1,1,0)   ← upper fan
  v0=(0,0,0)                 ← singular/bowtie vertex
  v3=(1,-1,0) v4=(-1,-1,0)  ← lower fan
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me070",
             title="duplicate_singular_vertices: minimal bowtie — 2-fan vertex in XY plane",
             defect_class="non_manifold_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — singular bowtie vertex
v1 = m.vertex(1.0, 1.0, 0.0)   # 1 — upper fan
v2 = m.vertex(-1.0, 1.0, 0.0)  # 2 — upper fan
v3 = m.vertex(1.0, -1.0, 0.0)  # 3 — lower fan
v4 = m.vertex(-1.0, -1.0, 0.0) # 4 — lower fan

t0 = m.triangle(v0, v1, v2)   # upper fan
t1 = m.triangle(v0, v3, v4)   # lower fan — shares only v0

# All four edges incident on v0 are boundary edges (shared by exactly 1 triangle).
m.assert_edge_shared(v0, v1, 1)   # boundary — only in t0
m.assert_edge_shared(v0, v2, 1)   # boundary — only in t0
m.assert_edge_shared(v0, v3, 1)   # boundary — only in t1
m.assert_edge_shared(v0, v4, 1)   # boundary — only in t1
# The vertex fan at v0 is disconnected: 2 triangles, 2 separate link components.
m.assert_vertex_fan_disconnected(v0)
