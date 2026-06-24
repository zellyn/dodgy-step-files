"""Me1090 — degree3_cap_minimal: apex with degree 3 in flat cap triggers remove_center_vertex (Branch 7).

CGAL PMP.remove_degenerate_faces Branch 7 @ line 2186 — *degree-3-vertex-in-cap*:
  'if (degree == 3) { Euler::remove_center_vertex(h, tmesh); }'
  — when the apex vertex has exactly 3 incident triangles CGAL collapses them
  via the remove_center_vertex Euler operator, replacing the 3-face fan with
  a single outer boundary triangle.

Defect pattern: apex v0 at (0.5, 0.289, 0.0) sits exactly in the z=0 plane with
  base triangle v1=(0,0,0), v2=(1,0,0), v3=(0.5,0.577,0). All three are nearly
  collinear (v0 is centroid of the base triangle projected to z=0) — the three
  fan triangles have very small but non-zero area. The apex has degree == 3 (three
  incident edges to v1, v2, v3). Each apex–base edge is shared by exactly 2 triangles
  (interior); each outer base edge is a boundary edge (shared by 1 triangle).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1090",
             title="degree-3 vertex cap: apex degree==3 in flat fan — remove_center_vertex branch",
             defect_class="degenerate_triangle")

# Apex: centroid of base equilateral triangle, at z=0 (flat cap — zero area faces).
# Use tiny z offset so triangles are well-defined but nearly degenerate.
apex = m.vertex(0.5, 0.289, 0.0001)   # 0 — degree-3 center vertex

# Base triangle (equilateral-ish, unit size).
v1 = m.vertex(0.0, 0.0, 0.0)          # 1
v2 = m.vertex(1.0, 0.0, 0.0)          # 2
v3 = m.vertex(0.5, 0.577, 0.0)        # 3

# Three fan triangles — apex is shared by exactly 3.
t0 = m.triangle(apex, v1, v2)   # face 0
t1 = m.triangle(apex, v2, v3)   # face 1
t2 = m.triangle(apex, v3, v1)   # face 2

# Interior fan edges: each shared by 2 triangles.
m.assert_edge_shared(apex, v1, 2)
m.assert_edge_shared(apex, v2, 2)
m.assert_edge_shared(apex, v3, 2)

# Outer boundary edges: each shared by only 1 triangle.
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v1, 1)
