"""Me1174 — Basic_TMesh.forceNormalConsistence adjacent_triangle_missing:
  adjacent triangle slot e->t2 is not NULL → propagation continues to neighbor
  (Branch 2).

MeshFix `Basic_TMesh.forceNormalConsistence` Branch 2 (*adjacent_triangle_missing*)
  @ line 950:
  'if (e->t2 != NULL) {' —
  For each edge of the current triangle, forceNormalConsistence checks if a
  neighbor exists at the edge's t2 slot. If e->t2 is not NULL, the function
  continues into the orientation-propagation block for that neighbor.
  Branch 2 fires when a real neighbor is present (the common case in an
  interior mesh).

Defect pattern: an open manifold mesh with two triangles sharing one interior
  edge. The interior edge has both t1 (t0) and t2 (t1) set. When
  forceNormalConsistence processes t0, it iterates t0's three edges. For the
  shared interior edge, e->t2 is NOT NULL (Branch 2 fires), so it inspects
  the adjacent triangle t1 for orientation consistency.
  The two triangles have consistent normals, so no seam is cut.

Geometry: two triangles sharing edge v1-v2.
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(0,1,0)
  t0=(v0,v1,v2) CCW, t1=(v2,v1,v3) CCW — consistent winding.
  Shared edge v1-v2: e->t2 = t1 (not NULL) → Branch 2 fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1174",
    title="Basic_TMesh.forceNormalConsistence adjacent_triangle_missing: e->t2 not NULL fires propagation to neighbor; two-triangle manifold (Branch 2)",
    defect_class="inverted_normal",
)

# Four vertices, two triangles sharing v1-v2
v0 = m.vertex(0.0,  0.0,  0.0)   # 0 — left base
v1 = m.vertex(1.0,  0.0,  0.0)   # 1 — right base
v2 = m.vertex(0.5,  1.0,  0.0)   # 2 — shared apex
v3 = m.vertex(0.0,  1.0,  0.0)   # 3 — left apex

# Two consistently-oriented CCW triangles
t0 = m.triangle(v0, v1, v2)   # 0: normal +Z
t1 = m.triangle(v2, v1, v3)   # 1: normal +Z (CCW shares v1-v2 reversed as interior edge)

# Interior shared edge (n=2)
m.assert_edge_shared(v1, v2, 2)

# Boundary edges (n=1 each)
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# Open strip: V=4, E=5, F=2, chi=1
m.assert_euler_characteristic(4, 5, 2, 1)
