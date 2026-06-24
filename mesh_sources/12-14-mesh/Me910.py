"""Me910 — di_cell.selectIntersections redundant-pair-test-detection: pair already cached in t->info; containsNode skips re-test (Branch 1).

MeshFix `di_cell.selectIntersections` Branch 1 (*Redundant pair-test detection*) @ line 119:
  'if (t->info != NULL && t->info->containsNode(s)) continue;'
  — when an octree cell processes a (triangle t, triangle s) pair that was already
  recorded in t->info by a prior cell (because both triangles straddle the cell
  boundary and appear in multiple cells), the containsNode check returns true and
  the intersection test is skipped for this cell. The fixture models two crossing
  triangles whose bounding boxes overlap the same spatial region, guaranteeing the
  pair would be encountered in more than one di_cell during the octree traversal.

Defect pattern: two triangles with a proper transverse self-intersection. Their
  shared-crossing geometry spans the spatial boundary between at least two octree
  cells, so di_cell.selectIntersections will encounter (t0, t1) in cell A and then
  attempt the same pair in cell B. On the second encounter t0->info already contains
  the node for t1 — containsNode(t1) == true → Branch 1 fires and the test is skipped.

Geometry:
  v0=(-1, 0, 0), v1=(1, 0, 0), v2=(0, 0, 2)  — flat horizontal triangle t0 in XZ
  v3=(0,-1, 1),  v4=(0, 1, 1), v5=(2, 0, 1)  — t1 pierces t0 along y-axis at (0,0,1)
  t0 and t1 cross transversally; both straddle the XZ midplane so both cells
  on either side of y=0 see this pair.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me910",
    title="di_cell.selectIntersections redundant-pair-test: crossing pair cached in t->info; containsNode returns true → second-cell test skipped (Branch 1)",
    defect_class="self_intersection_face_pair",
)

# t0: flat triangle in XZ plane at y=0, spanning y=0 boundary.
v0 = m.vertex(-1.0, 0.0, 0.0)   # 0
v1 = m.vertex( 1.0, 0.0, 0.0)   # 1
v2 = m.vertex( 0.0, 0.0, 2.0)   # 2

# t1: near-vertical triangle crossing t0 at z=1, straddling y=0.
v3 = m.vertex( 0.0,-1.0, 1.0)   # 3
v4 = m.vertex( 0.0, 1.0, 1.0)   # 4
v5 = m.vertex( 2.0, 0.0, 1.0)   # 5

t0 = m.triangle(v0, v1, v2)   # 0: horizontal-ish triangle in XZ
t1 = m.triangle(v3, v4, v5)   # 1: crossing triangle; edge (v3,v4) pierces t0 at (0,0,1)

# No shared vertices or edges — purely geometric crossing.
m.assert_vertex_pair_no_shared_triangle(v0, v3)
m.assert_vertex_pair_no_shared_triangle(v1, v4)

# The pair constitutes a proper self-intersection; both triangles straddle
# the y=0 spatial boundary, causing them to appear in two di_cells (y<0 and y>0).
# Branch 1 fires on the second cell encounter: containsNode(t1) == true → skip.
m.assert_triangles_self_intersect(t0, t1)
