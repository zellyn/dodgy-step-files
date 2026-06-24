"""Me1144 — volume_connected_components nested_component_orientation: child same orientation as parent violates nesting invariant (Branch 5).

CGAL PMP `PMP.volume_connected_components` Branch 5 (*nested_component_orientation*) @ line 800:
  'if(is_outer_volume == PMP::is_outward_oriented(child_cc, pmesh, np))
   { output.nested_orientation_errors.push_back(child_cc); continue; }'
  — after nesting depth is assigned, the orientation of each child component
  is validated against its parent. A child component correctly nested INSIDE a
  parent volume should have its normals pointing INWARD (opposite to the parent's
  outward normals). If the child has the SAME outward orientation as the parent,
  the nesting invariant is violated and Branch 5 fires.

Defect pattern: two nested closed tetrahedra where the inner (child) tetrahedron
  is wound with OUTWARD normals — the same orientation as the outer (parent)
  tetrahedron. A correct "inner shell" of a nested volume should have its normals
  pointing INWARD (toward the enclosed space), but the defect here is that the
  inner tet is wound with outward normals just like the outer tet. When
  volume_connected_components checks that the child orientation is OPPOSITE to the
  parent orientation, the check fails → Branch 5 fires.

Geometry:
  Outer tetrahedron: O0=(0,0,0), O1=(8,0,0), O2=(4,8,0), O3=(4,4,8).
    Wound with outward normals (CCW from outside) — correct parent orientation.
  Inner tetrahedron: I0=(2,1,1), I1=(4,1,1), I2=(3,3,1), I3=(3,2,3).
    Also wound with outward normals (CCW from outside of inner tet) — this is
    the DEFECT: for a nested inner shell the normals should point inward (CW from
    outside). The child has the same outward orientation as the parent → Branch 5.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1144",
    title="volume_connected_components nested_component_orientation: inner tetrahedron has same outward orientation as outer; nesting invariant violated; nested_orientation_error flagged (Branch 5)",
    defect_class="nested_orientation_mismatch",
)

# Outer tetrahedron (large shell, outward normals — correct parent orientation).
o0 = m.vertex(0.0, 0.0, 0.0)   #  0
o1 = m.vertex(8.0, 0.0, 0.0)   #  1
o2 = m.vertex(4.0, 8.0, 0.0)   #  2
o3 = m.vertex(4.0, 4.0, 8.0)   #  3 — apex

# Outer tet faces (CCW from outside → outward normals → correct parent).
ot0 = m.triangle(o0, o2, o1)   #  0 — outer bottom
ot1 = m.triangle(o0, o1, o3)   #  1 — outer front
ot2 = m.triangle(o1, o2, o3)   #  2 — outer right
ot3 = m.triangle(o2, o0, o3)   #  3 — outer left

# Inner tetrahedron (small, inside outer tet, same outward orientation — the DEFECT).
# A correct inner shell would use CW winding (inward normals). Instead we use
# the same CCW-from-outside winding as the outer tet → Branch 5 fires.
i0 = m.vertex(2.0, 1.0, 1.0)   #  4
i1 = m.vertex(4.0, 1.0, 1.0)   #  5
i2 = m.vertex(3.0, 3.0, 1.0)   #  6
i3 = m.vertex(3.0, 2.0, 3.0)   #  7 — inner apex

# Inner tet faces wound CCW from outside (same as parent — the orientation defect).
# A correctly nested inner shell would be: it0=(i0,i1,i2), it1=(i0,i3,i1), etc.
# (inward normals). Here we use the same outward-normal winding as the outer tet.
it0 = m.triangle(i0, i2, i1)   #  4 — inner bottom (outward normal → DEFECT for child)
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

# Inner tet is unreachable from outer tet (two disconnected closed components).
m.assert_triangle_not_reachable_from(it0, ot0)

# Euler for two disjoint closed sphere-topology manifolds: V=8, E=12, F=8, chi=4.
m.assert_euler_characteristic(8, 12, 8, 4)
