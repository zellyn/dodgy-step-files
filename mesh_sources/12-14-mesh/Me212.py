"""Me212 — cutAndStitch_orientation_inconsistency: adjacent triangles with opposite normals.

MeshFix `Basic_TMesh.cutAndStitch` Branch 3 (*ORIENTATION_INCONSISTENCY*) @ line 1003:
  'forceNormalConsistence()'
  After edge duplication, the mesh may contain non-orientable seams where
  adjacent triangles have inconsistent face normals. cutAndStitch calls
  forceNormalConsistence() to unify orientation before proceeding to stitch.

Defect pattern: two triangles share an edge but have opposite winding orders,
producing antiparallel normals at the shared edge. This is the case that
forceNormalConsistence() is designed to detect and correct.

Geometry: two triangles sharing edge (v0,v1) with deliberately reversed winding.
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(0.5,-1,0)
  t0=(v0,v1,v2) — CCW winding; normal points +Z
  t1=(v0,v1,v3) — CW winding at the shared edge; normal points -Z
  Both share edge (v0,v1) as an interior edge.

The normals of t0 and t1 point in opposite directions (inconsistent winding),
which is detected by forceNormalConsistence() in cutAndStitch Branch 3.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me212",
             title="cutAndStitch_orientation_inconsistency: adjacent triangles have inconsistent normals",
             defect_class="inverted_normal")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — above baseline
v3 = m.vertex(0.5, -1.0, 0.0)  # 3 — below baseline

t0 = m.triangle(v0, v1, v2)   # 0 — CCW; normal = +Z
t1 = m.triangle(v0, v1, v3)   # 1 — shares edge (v0,v1) with CW orientation relative to t0

# Edge (v0,v1) is interior — shared by both triangles.
m.assert_edge_shared(v0, v1, 2)

# t0 and t1 share the edge (v0,v1) but have inconsistent winding.
# forceNormalConsistence() target: these two triangles have antiparallel normals.
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)

# All outer edges are boundary.
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v0, v3, 1)
