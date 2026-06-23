"""Me191 — splitTriangle_new_triangle_from_e2_e1: nt2 created from e2 and e1 sides.

MeshFix `Basic_TMesh.splitTriangle` Branch 2 (*new_triangle_from_e2_e1*) @ line 1920:
  'nt2 = newTriangle(nv, v2, v1)'
  After creating nt1 from the e3/e1 corner, the second new child triangle nt2
  is created from the e1/e2 corner using vertices nv, v2, v1. This is the
  second of the three child triangles produced by the 3-way interior split.

Geometry: same canonical split as Me190. The new vertex nv is inserted into
triangle t(v0,v1,v2), producing three child triangles. Here we focus on nt2
as the carrier of the branch 2 defect.

Post-split layout:
  t   := (v0, v1, nv)   index 0 — original slot (e2 side)
  nt1 := (nv, v2, v0)   index 1 — first new triangle (e3/e1 corner)
  nt2 := (nv, v1, v2)   index 2 ← Branch 2: second new triangle (e2/e1 corner)

Defect: the pre-split mesh has triangle t(v0,v1,v2) and an interior vertex nv
not yet connected into the mesh — a suspended-vertex split-readiness condition.
nt2 is the triangle that MeshFix would allocate at line 1920.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me191",
             title="splitTriangle_new_triangle_from_e2_e1: second child triangle nt2 connects nv to v1-v2 side",
             defect_class="split_triangle_interior_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2
nv = m.vertex(1.0, 0.7, 0.0)   # 3 — interior vertex

t0  = m.triangle(v0, v1, nv)   # 0 — reused original slot
nt1 = m.triangle(nv, v2, v0)   # 1 — first child (e3/e1)
nt2 = m.triangle(nv, v1, v2)   # 2 — Branch 2: second child nt2 (e2/e1)

# Confirm nt2's outer edge (v1,v2) = e1 is a boundary edge (only in nt2).
m.assert_edge_shared(v1, v2, 1)   # e1: boundary — nt2's outer edge

# The ne1 inner edge (nv,v1) is shared between t0 and nt2.
m.assert_edge_shared(nv, v1, 2)   # ne1: shared by t0 and nt2

# The ne3 inner edge (nv,v2) is shared between nt1 and nt2.
m.assert_edge_shared(nv, v2, 2)   # ne3: shared by nt1 and nt2

# Confirm nt2 is adjacent to nt1 via ne3 (both share edge nv-v2).
m.assert_edge_shared(nv, v2, 2)   # ne3: shared — nt1 and nt2 neighbour each other

# Original outer edge v0-v1 (e2) is boundary (only in t0).
m.assert_edge_shared(v0, v1, 1)   # e2: boundary

# Original outer edge v2-v0 (e3) is boundary (only in nt1).
m.assert_edge_shared(v2, v0, 1)   # e3: boundary
