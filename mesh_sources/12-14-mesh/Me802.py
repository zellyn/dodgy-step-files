"""Me802 — is_polygon_soup_a_polygon_mesh orientation_consistency: adjacent polygons share same directed halfedge (Branch 3).

CGAL PMP `PMP.is_polygon_soup_a_polygon_mesh` Branch 3 (*orientation_consistency*) @ line 227:
  'if(fill_edge_map(polygon, edge_map) ==
   Polygon_soup_to_polygon_mesh_err::INCOMPATIBLE_ORIENTATION) return false;'
  — fill_edge_map records every directed halfedge (src→tgt) from each polygon into
  edge_map. If a directed halfedge already exists in the map (same direction, same
  src and tgt) the orientation is incompatible and Branch 3 fires immediately.

Defect pattern: two triangles that share physical edge {v1,v2} but both traverse it
  in the same direction (v1→v2). In a consistently oriented mesh adjacent triangles
  must use opposite halfedge directions on a shared edge (one uses v1→v2 and the
  other uses v2→v1). When both use v1→v2, fill_edge_map sees a collision and returns
  INCOMPATIBLE_ORIENTATION.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(1.5,1,0).
  t0=(v0,v1,v2): halfedges v0→v1, v1→v2, v2→v0. Normal = (0,0,+1).
  t1=(v3,v1,v2): halfedges v3→v1, v1→v2, v2→v3. Normal = (0,0,-1).
  Both emit directed halfedge v1→v2 → fill_edge_map collision → Branch 3 fires.
  Normals have opposite Z sign → dot product < 0 → inconsistent winding confirmed.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me802",
    title="is_polygon_soup_a_polygon_mesh orientation_consistency: t0 and t1 both traverse halfedge v1→v2; fill_edge_map returns INCOMPATIBLE_ORIENTATION (Branch 3)",
    defect_class="inconsistent_face_orientation",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — shared edge start (same direction in both triangles)
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — shared edge end
v3 = m.vertex(1.5, 1.0, 0.0)   # 3 — far vertex of t1

# t0: (v0,v1,v2) — emits halfedge v1→v2. Normal = (0,0,+1).
t0 = m.triangle(v0, v1, v2)

# t1: (v3,v1,v2) — also emits halfedge v1→v2. Normal = (0,0,-1).
# Both polygons use the same directed halfedge v1→v2 → INCOMPATIBLE_ORIENTATION.
t1 = m.triangle(v3, v1, v2)

# Normals are antiparallel (dot < 0) — the orientation inconsistency is geometric.
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)
