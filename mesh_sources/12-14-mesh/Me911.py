"""Me911 — di_cell.selectIntersections proper-vs-improper-intersection: justproper flag; touching (shared-vertex) pair is improper, transverse crossing is proper (Branch 2).

MeshFix `di_cell.selectIntersections` Branch 2 (*Proper vs improper intersection*) @ line 121:
  'if (!t->intersects(s, justproper)) continue;'
  — the `justproper` flag controls whether only transverse (proper) crossings are
  reported or also touching contacts (shared-vertex / shared-edge tangencies). When
  justproper=true, a pair that merely touches at a vertex passes the `intersects`
  test as false → Branch 2 fires and the touching pair is excluded. When
  justproper=false, touching pairs are also collected as intersecting.

Defect pattern: two triangle pairs in the same mesh:
  (t0, t1): t0 and t1 share exactly one vertex v2 and their interiors are disjoint.
    With justproper=true, this touching-only contact is IMPROPER → skipped.
  (t0, t2): t0 and t2 share no vertices; edge (v5,v6) of t2 pierces t0's interior
    at (1, 0.3, 0). This is a PROPER transverse intersection → collected.
  Branch 2 distinguishes these two cases via the justproper flag.

Geometry:
  t0: (v0=(0,0,0), v1=(1,1,0), v2=(2,0,0)) — flat in XY plane at z=0.
  t1: (v2=(2,0,0), v3=(3,1,0), v4=(4,0,0)) — shares only vertex v2, no crossing.
  t2: (v5=(1,0.3,-1), v6=(1,0.3,1), v7=(4,0,0)) — edge (v5,v6) pierces t0 at (1,0.3,0).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me911",
    title="di_cell.selectIntersections proper-vs-improper: shared-vertex touching pair is improper (justproper=true skips); transverse pair is proper (Branch 2)",
    defect_class="shared_vertex_adjacent_faces",
)

# t0: flat triangle in XY plane at z=0.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 1.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2: shared vertex between t0 and t1

# t1: adjacent triangle sharing only v2 — IMPROPER (touching only).
v3 = m.vertex(3.0, 1.0, 0.0)   # 3
v4 = m.vertex(4.0, 0.0, 0.0)   # 4

# t2: separate triangle whose edge (v5,v6) pierces t0's interior — PROPER crossing.
# Edge (v5,v6) is a vertical segment at (1, 0.3) in XY, from z=-1 to z=+1.
# It crosses t0's XY-plane face at (1, 0.3, 0), which is inside t0's interior
# (barycentric coords: u≈0.3, v≈0.2, w≈0.5 — all positive, sum=1).
v5 = m.vertex(1.0, 0.3,-1.0)   # 5: below t0
v6 = m.vertex(1.0, 0.3, 1.0)   # 6: above t0
v7 = m.vertex(4.0, 0.0, 0.0)   # 7: far vertex of t2 (same coords as v4, but distinct index)

t0 = m.triangle(v0, v1, v2)    # 0: hub flat triangle
t1 = m.triangle(v2, v3, v4)    # 1: shares only v2 with t0 (touching → improper)
t2 = m.triangle(v5, v6, v7)    # 2: no shared vertex; edge (v5,v6) pierces t0 (proper)

# t0 and t1 share only vertex v2 (index 2) — no shared edge.
m.assert_vertex_pair_no_shared_triangle(v0, v3)  # v0 in t0 only, v3 in t1 only
m.assert_vertex_pair_no_shared_triangle(v1, v4)  # v1 in t0 only, v4 in t1 only

# t0 and t2 share no vertices — purely geometric crossing.
m.assert_vertex_pair_no_shared_triangle(v0, v5)  # t0 and t2 disjoint vertices
m.assert_vertex_pair_no_shared_triangle(v1, v6)

# Touching pair (t0, t1): only vertex contact → IMPROPER; no geometric crossing.
# justproper=true → Branch 2 continues (skip); this pair is NOT collected.
m.assert_triangles_do_not_intersect(t0, t1)

# Proper crossing pair (t0, t2): edge (v5,v6) pierces t0's interior at (1,0.3,0).
# justproper=true → Branch 2 does NOT skip; collected as proper SI.
m.assert_triangles_self_intersect(t0, t2)
