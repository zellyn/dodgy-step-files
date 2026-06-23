"""Me333 — pinch_interior_edge_asymmetry_t1: interior edge with t1 set, mirror edge has t2 — merge.

MeshFix `Basic_TMesh.pinch` Branch 4 (*INTERIOR_EDGE_ASYMMETRY*) @ line 940:
  'if (e1->t1 != NULL) { if (e2->t2 != NULL) { ... e1->merge(e2); return true; } }'
  The interior edge e1 has t1 attached. The algorithm scans for a mirror edge e2
  such that e2->t2 is set (the other orientation). When found, the two edges are
  merged to eliminate the interior asymmetry (one side had t1 but no t2 from e2's
  perspective, and vice versa). This is the t1-side case.

Defect pattern: two adjacent triangles share a common edge but from opposing
  orientations — one triangle sees the edge as its t1 slot and the other sees
  it as its t2 slot in a non-manifold interior configuration.

Geometry: three coplanar triangles. The edge (v1,v3) is a manifold interior
  edge (n=2), and the edge (v0,v3) is also interior (n=2 — shared by t0 and t2).
  The structural pattern with t0 having both (v0,v3) shared with t2 and (v1,v3)
  shared with t1 represents the t1-side asymmetry: e1->t1 != NULL triggers
  the Branch 4 check for a mirror with e2->t2.

  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0), v3=(1,1,0), v4=(0,1,0)
  t0=(v0,v1,v3): left triangle
  t1=(v1,v2,v3): right triangle
  t2=(v0,v3,v4): upper left triangle
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me333",
             title="pinch_interior_edge_asymmetry_t1: e1->t1 set, mirror e2->t2 set — merge resolves asymmetry",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(1.0, 1.0, 0.0)   # 3
v4 = m.vertex(0.0, 1.0, 0.0)   # 4

t0 = m.triangle(v0, v1, v3)   # 0 — left
t1 = m.triangle(v1, v2, v3)   # 1 — right
t2 = m.triangle(v0, v3, v4)   # 2 — upper left

# Interior edge (v1,v3): shared by t0 and t1 — e1->t1 side.
m.assert_edge_shared(v1, v3, 2)

# Interior edge (v0,v3): shared by t0 and t2 — mirror e2->t2 side.
m.assert_edge_shared(v0, v3, 2)

# Boundary edges (each incident on exactly 1 triangle).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v0, v4, 1)
