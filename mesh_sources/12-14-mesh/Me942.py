"""Me942 — orient_polygon_soup polygon_orientation_pass: orienter.orient() DFS reorient.

CGAL PMP `PMP.orient_polygon_soup` Branch 3 (*polygon_orientation_pass*) @ line 560:
  'orienter.orient();'
  — after filling the edge map, the DFS orientor traverses the polygon dual graph.
  Starting from polygon 0, each adjacent polygon is visited via shared edges and
  flipped if its winding is inconsistent with the already-oriented neighbor.
  Branch 3 fires when any pair of adjacent triangles has inconsistent winding
  (one must be reoriented by the DFS pass).

Defect pattern: two triangles sharing edge (v1,v2) but wound in opposite senses —
  t0 winds CCW (normal +Z) and t1 winds CW (normal −Z). orienter.orient() detects
  the inconsistency at their shared edge and flips t1 to restore a consistent CCW
  orientation. The oracle records the inconsistent-winding pair before fixing.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(1.5,1,0)
  t0=(v0,v1,v2)  CCW, normal +Z
  t1=(v1,v2,v3)  CW  (v2 before v3 reverses sense), normal −Z
  Shared edge (v1,v2) — n=2. orient() walks from t0 to t1 via this edge and flips t1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me942",
    title="orient_polygon_soup polygon_orientation_pass: t0 CCW + t1 CW share edge (v1,v2); orienter.orient() flips t1 via DFS (Branch 3)",
    defect_class="inconsistent_face_orientation",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left base
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — shared edge endpoint / right base
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — shared edge endpoint / apex
v3 = m.vertex(1.5, 1.0, 0.0)   # 3 — right apex

# t0 wound CCW: normal = (v1-v0)×(v2-v0) = (1,0,0)×(0.5,1,0) = (0,0,1) → +Z
t0 = m.triangle(v0, v1, v2)    # 0: CCW, normal +Z

# t1 wound CW: normal = (v2-v1)×(v3-v1) = (-0.5,1,0)×(0.5,1,0) = (0,0,-1) → -Z
t1 = m.triangle(v1, v2, v3)    # 1: CW (reversed), normal −Z — defect

# Shared interior edge (v1, v2) — n=2. DFS walks from t0 to t1 here.
m.assert_edge_shared(v1, v2, 2)

# Boundary edges — n=1 each.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# Inconsistent winding: t0 and t1 share edge (v1,v2) but have antiparallel normals.
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)

# Euler: V=4, E=5, F=2, chi=1 (open disk, two triangles).
m.assert_euler_characteristic(4, 5, 2, 1)
