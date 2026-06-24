"""Me941 — orient_polygon_soup edge_map_fill: orienter.fill_edge_map() builds edge→polygon map.

CGAL PMP `PMP.orient_polygon_soup` Branch 2 (*edge_map_fill*) @ line 559:
  'orienter.fill_edge_map();'
  — after storing initial_nb_pts, the orientor builds a map from each directed
  half-edge (vertex pair) to its owning polygon index. For a consistent polygon
  soup the map will contain each undirected edge once (manifold) or mark it as
  a candidate for non-manifold edges. Branch 2 fires when shared edges exist to
  populate the map.

Defect pattern: a four-triangle fan sharing a central hub vertex and three
  interior edges. The fan has three interior shared edges (each n=2) and five
  boundary edges (n=1). fill_edge_map() processes all six directed half-edges on
  the three interior edges, populating the edge→polygon adjacency structure for
  the subsequent DFS orientation pass.

Geometry:
  v0=(0,0,0) hub; v1=(1,0,0), v2=(0,1,0), v3=(-1,0,0), v4=(0,-1,0) rim.
  t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4), t3=(v0,v4,v1)
  Three interior edges: (v0,v1)n=2, (v0,v2)n=2, (v0,v3)n=2, (v0,v4)n=2.
  fill_edge_map() maps each directed pair to its polygon index.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me941",
    title="orient_polygon_soup edge_map_fill: four-triangle fan; orienter.fill_edge_map() populates 4 interior shared edges (Branch 2)",
    defect_class="inconsistent_face_orientation",
)

v0 = m.vertex(0.0,  0.0, 0.0)   # 0 — hub
v1 = m.vertex(1.0,  0.0, 0.0)   # 1 — right rim
v2 = m.vertex(0.0,  1.0, 0.0)   # 2 — top rim
v3 = m.vertex(-1.0, 0.0, 0.0)   # 3 — left rim
v4 = m.vertex(0.0, -1.0, 0.0)   # 4 — bottom rim

# Four CCW triangles forming a pinwheel fan around v0.
t0 = m.triangle(v0, v1, v2)   # 0: NE quadrant
t1 = m.triangle(v0, v2, v3)   # 1: NW quadrant
t2 = m.triangle(v0, v3, v4)   # 2: SW quadrant
t3 = m.triangle(v0, v4, v1)   # 3: SE quadrant

# Four interior hub edges — each shared by exactly 2 triangles.
# fill_edge_map() inserts directed pairs for all of these.
m.assert_edge_shared(v0, v1, 2)   # t0 ∩ t3
m.assert_edge_shared(v0, v2, 2)   # t0 ∩ t1
m.assert_edge_shared(v0, v3, 2)   # t1 ∩ t2
m.assert_edge_shared(v0, v4, 2)   # t2 ∩ t3

# Four outer rim edges — boundary (n=1 each).
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v1, 1)

# Euler: V=5, E=8, F=4, chi=1 (open disk).
m.assert_euler_characteristic(5, 8, 4, 1)
