"""Me943 — orient_polygon_soup vertex_duplication: orienter.duplicate_singular_vertices().

CGAL PMP `PMP.orient_polygon_soup` Branch 4 (*vertex_duplication*) @ line 561:
  'orienter.duplicate_singular_vertices();'
  — after the DFS orientation pass, the orientor calls duplicate_singular_vertices
  to split any non-manifold (singular/bowtie) vertex into one copy per connected
  fan. A singular vertex is one whose incident polygons form two or more disconnected
  fans — removing the vertex would disconnect the neighborhood. Duplication adds new
  entries to the points array, which is later detected by the manifoldness_check.

Defect pattern: a bowtie mesh — vertex v0 is shared by two completely disconnected
  triangle fans (upper fan and lower fan) with no edge connecting the fans at v0.
  v0's 1-ring is not a single connected component. duplicate_singular_vertices()
  splits v0 into two copies (v0_upper and v0_lower), one per fan, adding 1 new point
  to the points array.

Geometry:
  v0=(0,0,0) — bowtie hub (singular/non-manifold vertex)
  v1=(1,1,0), v2=(-1,1,0) — upper fan
  v3=(1,-1,0), v4=(-1,-1,0) — lower fan
  t0=(v0,v1,v2), t1=(v0,v2,v1) is degenerate; instead use minimal 1-tri fans:
  t0=(v0,v1,v2) upper fan triangle
  t1=(v0,v3,v4) lower fan triangle — shares only v0 with t0, no shared edge.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me943",
    title="orient_polygon_soup vertex_duplication: bowtie at v0; orienter.duplicate_singular_vertices() splits v0 into 2 copies (Branch 4)",
    defect_class="non_manifold_vertex",
)

v0 = m.vertex(0.0,  0.0, 0.0)   # 0 — bowtie hub: singular / non-manifold vertex
v1 = m.vertex(1.0,  1.0, 0.0)   # 1 — upper fan right
v2 = m.vertex(-1.0, 1.0, 0.0)   # 2 — upper fan left
v3 = m.vertex(1.0, -1.0, 0.0)   # 3 — lower fan right
v4 = m.vertex(-1.0,-1.0, 0.0)   # 4 — lower fan left

# Upper fan: one triangle around v0 above x-axis.
t0 = m.triangle(v0, v1, v2)    # 0: CCW, normal +Z

# Lower fan: one triangle around v0 below x-axis — no shared edge with t0.
t1 = m.triangle(v0, v3, v4)    # 1: CCW, normal +Z

# v0's fan is disconnected — the vertex is non-manifold (bowtie).
m.assert_vertex_fan_disconnected(v0)

# v0 edges in upper fan — each appears only once (n=1); no edge connects fans.
m.assert_edge_shared(v0, v1, 1)   # boundary — upper fan only
m.assert_edge_shared(v0, v2, 1)   # boundary — upper fan only
m.assert_edge_shared(v0, v3, 1)   # boundary — lower fan only
m.assert_edge_shared(v0, v4, 1)   # boundary — lower fan only

# After duplicate_singular_vertices(): points grows by 1; the lower fan
# gets a new vertex v0' at (0,0,0). Manifoldness check then detects the growth.
