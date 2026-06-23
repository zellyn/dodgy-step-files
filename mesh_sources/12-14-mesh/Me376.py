"""Me376 — isSelectionSimple_boundary_loop_complexity: nv != bdr.numels(), non-simple boundary (Branch 7).

MeshFix `Basic_TMesh.isSelectionSimple` Branch 7 (*boundary_loop_complexity*) @ line 1041:
  `if (nv != bdr.numels()) { ...; return 0; }` — after traversing the
  boundary loop of the selected region, the count of boundary vertices `nv`
  does not equal the count of boundary edges in `bdr`. For a simple closed
  loop, these must be equal (each vertex has exactly one successor edge).
  When nv != bdr.numels(), the boundary loop is non-simple (has more edges
  than vertices, e.g. a self-touching boundary or an extra inner loop).

The fixture models an annular (ring-shaped) selection: a central hole
surrounded by a ring of triangles. The selection boundary consists of two
separate loops — the outer boundary and the inner boundary (around the hole).
Combined, the boundary list has more edges (outer + inner) than there are
unique boundary vertices counted in the single traversal → nv != bdr.numels().

Geometry: a 6-triangle ring around a triangular hole:
  Inner vertices: v0=(0,0,0), v1=(1,0,0), v2=(0.5,0.87,0) — forming the hole
  Outer vertices: v3=(-1,-1,0), v4=(2,-1,0), v5=(0.5, 2,0)

  Six triangles connecting inner and outer rings:
  t0=(v0,v1,v3), t1=(v1,v4,v3) — bottom-left and bottom-right
  t2=(v1,v2,v4), t3=(v2,v5,v4) — right side
  t4=(v2,v0,v5), t5=(v0,v3,v5) — left side

The hole boundary (v0,v1,v2) has 3 edges (n=1 each — inner boundary).
The outer boundary (v3,v4,v5) has 3 edges (n=1 each — outer boundary).
Total: 6 boundary edges, 6 boundary vertices (outer) + 3 inner = but
the two separate loops make the boundary non-simple.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me376",
    title="isSelectionSimple_boundary_loop_complexity: annular selection with inner hole, two boundary loops → nv != bdr.numels() (Branch 7)",
    defect_class="selection_non_simple_boundary",
)

# Inner triangle vertices (form the hole boundary).
v0 = m.vertex(0.0,  0.0,  0.0)  # 0: inner
v1 = m.vertex(1.0,  0.0,  0.0)  # 1: inner
v2 = m.vertex(0.5,  0.87, 0.0)  # 2: inner (approx equilateral)

# Outer triangle vertices (form the outer boundary).
v3 = m.vertex(-1.0, -1.0, 0.0)  # 3: outer
v4 = m.vertex(2.0,  -1.0, 0.0)  # 4: outer
v5 = m.vertex(0.5,  2.0,  0.0)  # 5: outer

# Six ring triangles connecting inner and outer vertices.
# Bottom strip:
t0 = m.triangle(v0, v3, v1)  # 0: left-bottom
t1 = m.triangle(v1, v3, v4)  # 1: right-bottom
# Right strip:
t2 = m.triangle(v1, v4, v2)  # 2: right-lower
t3 = m.triangle(v2, v4, v5)  # 3: right-upper
# Left strip:
t4 = m.triangle(v2, v5, v0)  # 4: left-upper
t5 = m.triangle(v0, v5, v3)  # 5: left-lower

# Inner hole edges (each incident on exactly 1 triangle — the hole boundary).
m.assert_edge_shared(v0, v1, 1)  # bottom inner edge (t0 only)
m.assert_edge_shared(v1, v2, 1)  # right inner edge (t2 only)
m.assert_edge_shared(v0, v2, 1)  # left inner edge (t4 only)

# Outer boundary edges (n=1).
m.assert_edge_shared(v3, v4, 1)  # outer bottom (t1 only)
m.assert_edge_shared(v4, v5, 1)  # outer right (t3 only)
m.assert_edge_shared(v3, v5, 1)  # outer left (t5 only)

# Interior ring edges shared by adjacent ring triangles (n=2).
m.assert_edge_shared(v0, v3, 2)  # shared by t0 and t5
m.assert_edge_shared(v1, v3, 2)  # shared by t0 and t1
m.assert_edge_shared(v1, v4, 2)  # shared by t1 and t2
m.assert_edge_shared(v2, v4, 2)  # shared by t2 and t3
m.assert_edge_shared(v2, v5, 2)  # shared by t3 and t4
m.assert_edge_shared(v0, v5, 2)  # shared by t4 and t5

# Euler: V=6, E=12, F=6, chi=0.
# An annular strip (cylinder): chi = V-E+F = 6-12+6 = 0.
m.assert_euler_characteristic(6, 12, 6, 0)
