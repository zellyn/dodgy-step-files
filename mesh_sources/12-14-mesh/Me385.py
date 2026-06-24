"""Me385 — isDoubleFlat_singular_edge_case: exactly one ridge edge in 1-ring; nne==1 → return false.

MeshFix `Vertex.isDoubleFlat` Branch 6 (*singular_edge_case*) @ line 337:
  'else if (nne == 1) return false;'
  After the full 1-ring scan, if exactly one edge with non-zero convexity was
  found (nne==1), the configuration is a singular half-fold — one crease line
  emanating from v0 that cannot define a valid DoubleFlat (which needs a complete
  fold with two matched ridges). MeshFix returns false at Branch 6.

Geometric signature: vertex v0 at the center of an open fan of 4 triangles. The
first 3 triangles (t0, t1, t2) lie in the z=0 plane (flat). The 4th triangle t3
is raised (v5 has z>0). The edge (v0,v4) is shared by flat t2 and raised t3 —
this is the ONLY interior ridge edge. All other interior fan edges connect two
flat triangles (coplanar). Result: nne==1 after the full scan → Branch 6 fires.

Geometry:
  v0 = (0.0,  0.0,  0.0)   — center vertex
  v1 = (-1.0, 0.0,  0.0)   — flat, boundary start
  v2 = (-0.5, 1.0,  0.0)   — flat
  v3 = (0.5,  1.0,  0.0)   — flat
  v4 = (1.0,  0.0,  0.0)   — flat, boundary between flat and raised
  v5 = (1.5,  0.0,  1.0)   — raised, boundary end

  t0 = (v0, v1, v2)   — flat (z=0 plane)
  t1 = (v0, v2, v3)   — flat (z=0 plane)
  t2 = (v0, v3, v4)   — flat (z=0 plane)
  t3 = (v0, v4, v5)   — raised (v5 at z=1)

Fan edge summary:
  (v0,v1): boundary (n=1, only in t0)
  (v0,v2): interior (n=2, in t0 and t1) — flat-flat, no ridge
  (v0,v3): interior (n=2, in t1 and t2) — flat-flat, no ridge
  (v0,v4): interior (n=2, in t2 and t3) — flat/raised → RIDGE (nne=1)
  (v0,v5): boundary (n=1, only in t3)

nne==1 after full scan → Branch 6 → return false.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me385",
             title="isDoubleFlat_singular_edge_case: v0 has exactly one ridge edge (v0,v4) in open 4-triangle fan; nne==1 → Branch 6 returns false",
             defect_class="singular_half_fold_vertex")

v0 = m.vertex(0.0,  0.0,  0.0)   # 0 — center vertex
v1 = m.vertex(-1.0, 0.0,  0.0)   # 1 — flat, boundary start
v2 = m.vertex(-0.5, 1.0,  0.0)   # 2 — flat
v3 = m.vertex(0.5,  1.0,  0.0)   # 3 — flat
v4 = m.vertex(1.0,  0.0,  0.0)   # 4 — flat, boundary between flat and raised
v5 = m.vertex(1.5,  0.0,  1.0)   # 5 — raised

t0 = m.triangle(v0, v1, v2)    # 0 — flat
t1 = m.triangle(v0, v2, v3)    # 1 — flat
t2 = m.triangle(v0, v3, v4)    # 2 — flat
t3 = m.triangle(v0, v4, v5)    # 3 — raised

# Boundary edges of v0 (open fan ends):
m.assert_edge_shared(v0, v1, 1)   # boundary, only in t0
m.assert_edge_shared(v0, v5, 1)   # boundary, only in t3

# Interior fan edges at v0 (shared by 2 triangles):
m.assert_edge_shared(v0, v2, 2)   # t0 and t1 — flat-flat, no ridge
m.assert_edge_shared(v0, v3, 2)   # t1 and t2 — flat-flat, no ridge
m.assert_edge_shared(v0, v4, 2)   # t2(flat) and t3(raised) — single ridge (nne=1)

# Outer boundary edges (each in 1 triangle):
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
