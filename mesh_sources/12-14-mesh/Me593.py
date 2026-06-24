"""Me593 — holeFilling_TriangulateHole_normal_computation_failure: average normal of new triangles is null; skip optimization (Branch 4).

MeshFix `holeFilling::TriangulateHole@L157` Branch 4 (*NORMAL_COMPUTATION_FAILURE*) @ line 213:
  'nor.isNull()' → log "Unable to compute"; return nt.
  After creating new triangles to fill the hole, TriangulateHole computes
  the average normal of all new triangles to establish orientation. If the
  average normal is zero/null (triangles have anti-parallel normals that
  cancel out), the optimization phase (edge swaps) is skipped and the
  method returns early with the triangle count.

Defect pattern: a hole boundary whose filling triangles produce anti-parallel
  normals. This happens when the boundary vertices lie in a saddle configuration
  — some filling triangles face up (+Z) and others face down (-Z), and their
  normals cancel exactly to zero.

Geometry: a boundary cycle of 6 vertices arranged as a saddle — alternating
  vertices above and below z=0. Any triangulation of this cycle will produce
  some +Z and some -Z triangles whose normals sum to zero.

  v0=(0,0, 0.5), v1=(2,0,-0.5), v2=(3,1, 0.5),
  v3=(2,2,-0.5), v4=(0,2, 0.5), v5=(-1,1,-0.5)
  — hexagonal saddle with alternating z-heights.

  We provide 4 triangles forming a "butterfly" boundary around a central hole.
  Two triangles face up, two face down, creating the saddle boundary.

  Surrounding triangles (boundary-defining, not the fill):
  Left strip (below): t0=(v5,v0,v1) — going downward, normal points -Z.
  Right strip (above): t1=(v2,v3,v4) — normal points +Z.
  These two triangles share no edge but both connect to the same central hole.
  We model the configuration as two pairs of triangles around a central hole.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me593",
    title="holeFilling_TriangulateHole_normal_computation_failure: saddle-shaped hole boundary produces anti-parallel fill normals summing to zero; nor.isNull fires (Branch 4)",
    defect_class="hole_in_hull",
)

# Saddle hexagon: alternating z heights create anti-parallel normals on fill triangles.
v0 = m.vertex(0.0,  0.0,  0.5)   # 0: up
v1 = m.vertex(2.0,  0.0, -0.5)   # 1: down
v2 = m.vertex(3.0,  1.0,  0.5)   # 2: up
v3 = m.vertex(2.0,  2.0, -0.5)   # 3: down
v4 = m.vertex(0.0,  2.0,  0.5)   # 4: up
v5 = m.vertex(-1.0, 1.0, -0.5)   # 5: down

# 6 boundary triangles forming the saddle rim around the central hole.
# Each triangle connects two adjacent boundary vertices + one more, leaving
# the central hexagonal hole open.
# We use a minimal set of 6 rim triangles (one per boundary edge).
# Hub vertex at center at z=0 for the rim triangles only (not filling the hole).
vh = m.vertex(1.0, 1.0, 0.0)   # 6: hub for rim triangles

t0 = m.triangle(v0, v1, vh)   # 0: rim lower-right — normal mixed
t1 = m.triangle(v1, v2, vh)   # 1: rim right — +Z bias
t2 = m.triangle(v2, v3, vh)   # 2: rim upper-right — -Z bias
t3 = m.triangle(v3, v4, vh)   # 3: rim upper-left — +Z bias
t4 = m.triangle(v4, v5, vh)   # 4: rim left — -Z bias
t5 = m.triangle(v5, v0, vh)   # 5: rim lower-left — +Z bias

# Hub edges — each shared by exactly 2 rim triangles.
m.assert_edge_shared(v0, vh, 2)
m.assert_edge_shared(v1, vh, 2)
m.assert_edge_shared(v2, vh, 2)
m.assert_edge_shared(v3, vh, 2)
m.assert_edge_shared(v4, vh, 2)
m.assert_edge_shared(v5, vh, 2)

# Outer boundary edges — each on exactly 1 rim triangle.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, v0, 1)

# Outer boundary cycle: saddle hexagon with alternating +/- z heights.
m.assert_hole_boundary([v0, v1, v2, v3, v4, v5])

# Euler: V=7, E=12, F=6, chi=1 (open disk — central hole).
m.assert_euler_characteristic(7, 12, 6, 1)
