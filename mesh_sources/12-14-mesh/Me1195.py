"""Me1195 — is_polygon_soup_a_polygon_mesh orientation_consistency:
  adjacent polygons do not share opposite halfedges; orientation check fails (Branch 3).

CGAL PMP `PMP.is_polygon_soup_a_polygon_mesh` Branch 3 (*orientation_consistency*)
  @ line 227:
  'if (fill_edge_map(points, polygons) != 0) return false' —
  After checking for repeated vertices (Branch 1) and non-manifold edges
  (Branch 2), Branch 3 calls fill_edge_map to check orientation consistency.
  Two adjacent polygons sharing an undirected edge must traverse it in opposite
  directions (one as (i,j) and the other as (j,i)). If both traverse in the
  same direction, fill_edge_map detects a non-manifold directed edge and
  returns non-zero, triggering Branch 3 to return false.

Defect pattern: two triangles sharing edge v1-v2 but both oriented the same way
  (both CCW in the XY plane) — they both traverse the directed edge v1→v2.
  This means fill_edge_map sees directed edge (1,2) twice (from both triangles),
  which is non-manifold for orientation consistency. Branch 3 fires.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(1.5,1,0)
  t0=(v0,v1,v2) — CCW: directed edges v0→v1, v1→v2, v2→v0
  t1=(v3,v1,v2) — same CCW: directed edges v3→v1, v1→v2, v2→v3
  Both t0 and t1 traverse directed edge v1→v2 — inconsistent orientation.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1195",
    title="is_polygon_soup_a_polygon_mesh orientation_consistency: two adjacent triangles both traverse edge v1→v2 in same direction; fill_edge_map returns non-zero; returns false (Branch 3)",
    defect_class="non_manifold_edge",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left base
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — middle base
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — shared apex
v3 = m.vertex(1.5, 1.0, 0.0)   # 3 — right outer

# Both triangles traverse edge v1→v2 in the same directed sense
t0 = m.triangle(v0, v1, v2)    # 0: directed edges v0→v1, v1→v2, v2→v0
t1 = m.triangle(v3, v1, v2)    # 1: directed edges v3→v1, v1→v2, v2→v3

# The shared edge v1-v2 is traversed in the SAME direction by both triangles
# (both CCW from above), so fill_edge_map sees (1,2) twice — non-manifold directed edge
m.assert_edge_shared(v1, v2, 2)   # 2 triangles share this edge (orientation wrong)

# The inconsistent winding means adjacent normals are parallel, not anti-parallel
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)

# Other edges
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# V=4, E=5, F=2, chi=1
m.assert_euler_characteristic(4, 5, 2, 1)
