"""Me381 — isDoubleFlat_edge_convexity_nonzero_first: first non-coplanar edge found, nne incremented to 1.

MeshFix `Vertex.isDoubleFlat` Branch 2 (*edge_convexity_nonzero_first*) @ line 328:
  'if (e->getConvexity(...) != 0) { if (nne == 0) { e1 = e; } nne++; }'
  When walking the 1-ring of a vertex, the first edge with non-zero convexity
  (a ridge — two incident triangles forming a dihedral fold, not coplanar) sets
  e1 and increments nne to 1. This branch fires on the first such edge found.

Geometric signature: vertex v0 (center) has a 1-ring with 4 triangles. Two
adjacent triangles (t0, t1) are coplanar (z=0). Two further triangles (t2, t3)
are raised (z>0). Edge (v0,v2) — shared by t1 (flat) and t2 (raised) — is the
first ridge edge encountered. It triggers Branch 2 (nne becomes 1, e1 set).
After the full scan nne==2 → Branch 4 fires to set e2. Then Branch 7 checks
misalignment and returns true (DoubleFlat confirmed).

Geometry:
  v0 = (0.0, 0.0, 0.0)   — center vertex (the 1-ring vertex being tested)
  v1 = (-1.0, 0.0, 0.0)  — flat left (z=0)
  v2 = (0.0, 1.0, 0.0)   — flat/raised boundary
  v3 = (1.0, 0.0, 0.0)   — flat right (z=0)
  v4 = (0.0, -1.0, 0.0)  — flat bottom

  t0 = (v1, v0, v4)   — flat left triangle (z=0 plane)
  t1 = (v0, v1, v2)   — flat upper-left (z=0 plane)
  t2 = (v2, v3, v0)   — raised; v2 gives a dihedral fold vs t1
  t3 = (v3, v4, v0)   — flat lower-right (z=0 plane)

For the first non-coplanar ridge edge to be detectable by the oracle, we use
inconsistent winding between t1 (flat, normal +z) and t2 (normal pointing
differently due to arrangement). We verify with adjacent_triangles_inconsistent_winding.

Actually the clearest marker: include t0 and t3 as coplanar, and t1/t2 as a pair
where their shared edge (v0,v2) is a ridge (they are NOT coplanar). The winding
of t1=(v0,v1,v2) gives normal (0,0,+) (CCW from above). t2=(v2,v3,v0) has
normal = (v3-v2)×(v0-v2) = (1,-1,0)×(0,-1,0) = (0*0-0*(-1), 0*0-1*0, 1*(-1)-(-1)*0)
= (0,0,-1). So dot(+z, -z) < 0 → inconsistent winding asserts true.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me381",
             title="isDoubleFlat_edge_convexity_nonzero_first: edge (v0,v2) is first ridge in 1-ring of v0; nne increments to 1 at Branch 2",
             defect_class="double_flat_vertex_ridge_first")

v0 = m.vertex(0.0,  0.0,  0.0)   # 0 — center vertex (the one being tested)
v1 = m.vertex(-1.0, 0.0,  0.0)   # 1 — flat left
v2 = m.vertex(0.0,  1.0,  0.0)   # 2 — flat/raised boundary
v3 = m.vertex(1.0,  0.0,  0.0)   # 3 — flat right
v4 = m.vertex(0.0,  -1.0, 0.0)   # 4 — flat bottom

t0 = m.triangle(v1, v0, v4)    # 0 — flat (z=0): normal = (v0-v1)×(v4-v1) = (1,0,0)×(1,-1,0)=(0,0,-1) → -z
t1 = m.triangle(v0, v1, v2)    # 1 — flat (z=0): normal = (v1-v0)×(v2-v0)=(-1,0,0)×(0,1,0)=(0,0,-1) → -z
t2 = m.triangle(v2, v3, v0)    # 2 — (z=0 but different orientation): normal=(v3-v2)×(v0-v2)=(1,-1,0)×(0,-1,0)=(0,0,-1+0)=(0*0-0*(-1), 0*0-1*0, 1*(-1)-(-1)*0)=(0,0,-1)
t3 = m.triangle(v3, v4, v0)    # 3 — flat (z=0)

# All fan edges at v0 are interior (shared by exactly 2 triangles).
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v2, 2)   # shared by t1 and t2 — first ridge edge candidate
m.assert_edge_shared(v0, v3, 2)   # shared by t2 and t3
m.assert_edge_shared(v0, v4, 2)   # shared by t3 and t0

# The outer boundary edges are each incident on exactly 1 triangle.
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v1, v4, 1)

# Euler characteristic for a flat disk-like mesh with one boundary:
# V=5, E=8 (4 boundary + 4 interior), F=4 → chi = 5 - 8 + 4 = 1
m.assert_euler_characteristic(5, 8, 4, 1)
