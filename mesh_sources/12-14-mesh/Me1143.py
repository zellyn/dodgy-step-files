"""Me1143 — volume_connected_components nesting_depth_assignment: ray-casting parity determines depth and volume_id (Branch 4).

CGAL PMP `PMP.volume_connected_components` Branch 4 (*nesting_depth_assignment*) @ line 720:
  'volume_id[cc] = 2 * parent_depth + (is_outer_volume ? 0 : 1);
   parent[cc] = parent_cc; ...'
  — for each closed, non-SI, correctly-oriented connected component, the function
  shoots rays to count how many other component surfaces the ray crosses. An even
  crossing count means the component is at an outer nesting level; an odd count
  means it is inside another component. The nesting depth determines the volume_id
  assignment: a depth-0 outer shell gets volume_id=0; a depth-1 inner shell (nested
  inside one outer shell) gets volume_id=2.

Defect pattern: two nested closed tetrahedra — an outer large tetrahedron
  enclosing a smaller inner tetrahedron. Both are closed, non-SI, and consistently
  oriented with outward normals. A ray from any interior point of the inner tet
  crosses 2 surfaces (inner tet face + outer tet face) → even parity → the INNER
  tet volume gets depth=1 → volume_id=2. Branch 4 fires for the inner component
  when its parent (outer tet) is identified and depth is assigned.

Geometry:
  Outer tetrahedron (large): vertices at O0=(0,0,0), O1=(8,0,0), O2=(4,8,0), O3=(4,4,8).
  Inner tetrahedron (small): vertices at I0=(2,1,1), I1=(4,1,1), I2=(3,3,1), I3=(3,2,3).
    The inner tet fits entirely within the outer tet's volume.

  Both tetrahedra are consistently wound with outward normals (CCW from outside).
  The two components are disconnected (no shared vertices or edges) — ray-casting
  identifies the inner as nested → Branch 4 assigns depth=1 to inner component.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1143",
    title="volume_connected_components nesting_depth_assignment: inner tetrahedron nested inside outer; ray-casting parity assigns volume_id=2 to inner component (Branch 4)",
    defect_class="nested_volume_components",
)

# Outer tetrahedron (large shell, outward normals).
o0 = m.vertex(0.0, 0.0, 0.0)   #  0 — outer base corner
o1 = m.vertex(8.0, 0.0, 0.0)   #  1 — outer base corner
o2 = m.vertex(4.0, 8.0, 0.0)   #  2 — outer base corner
o3 = m.vertex(4.0, 4.0, 8.0)   #  3 — outer apex

# Outer tet faces (CCW from outside → outward normals).
ot0 = m.triangle(o0, o2, o1)   #  0 — outer bottom (normal -Z)
ot1 = m.triangle(o0, o1, o3)   #  1 — outer front
ot2 = m.triangle(o1, o2, o3)   #  2 — outer right
ot3 = m.triangle(o2, o0, o3)   #  3 — outer left

# Inner tetrahedron (small shell, entirely inside outer tet, outward normals).
# Centroid ≈ (3, 1.75, 1.5) — well inside the outer tet.
i0 = m.vertex(2.0, 1.0, 1.0)   #  4 — inner base corner
i1 = m.vertex(4.0, 1.0, 1.0)   #  5 — inner base corner
i2 = m.vertex(3.0, 3.0, 1.0)   #  6 — inner base corner
i3 = m.vertex(3.0, 2.0, 3.0)   #  7 — inner apex

# Inner tet faces (CCW from outside of inner tet → outward normals).
it0 = m.triangle(i0, i2, i1)   #  4 — inner bottom (normal -Z, outward for inner)
it1 = m.triangle(i0, i1, i3)   #  5 — inner front
it2 = m.triangle(i1, i2, i3)   #  6 — inner right
it3 = m.triangle(i2, i0, i3)   #  7 — inner left

# Outer tet: all 6 edges shared by exactly 2 faces (closed manifold).
m.assert_edge_shared(o0, o1, 2)
m.assert_edge_shared(o0, o2, 2)
m.assert_edge_shared(o1, o2, 2)
m.assert_edge_shared(o0, o3, 2)
m.assert_edge_shared(o1, o3, 2)
m.assert_edge_shared(o2, o3, 2)

# Inner tet: all 6 edges shared by exactly 2 faces (closed manifold).
m.assert_edge_shared(i0, i1, 2)
m.assert_edge_shared(i0, i2, 2)
m.assert_edge_shared(i1, i2, 2)
m.assert_edge_shared(i0, i3, 2)
m.assert_edge_shared(i1, i3, 2)
m.assert_edge_shared(i2, i3, 2)

# Inner tet is unreachable from outer tet (two disconnected components).
m.assert_triangle_not_reachable_from(it0, ot0)

# Euler for each tet component: V=4, E=6, F=4, chi=2.
# Combined mesh: V=8, E=12, F=8, chi=4 (two disjoint spheres: 2+2=4).
m.assert_euler_characteristic(8, 12, 8, 4)
