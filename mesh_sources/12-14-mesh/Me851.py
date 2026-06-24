"""Me851 — does_bound_a_volume orientation_inconsistent: closed tetrahedron with one flipped face; does_orient_polygon_soup_to_bound_a_volume fails; returns false (Branch 2).

CGAL PMP `PMP.does_bound_a_volume` Branch 2 (*orientation_inconsistent*) @ line 922:
  'if(!PMP::does_bound_a_volume(tmesh, np)) return false;'
  — after confirming is_closed, the predicate checks whether the closed
  mesh has a consistent outward orientation. When one or more faces have
  reversed winding relative to their neighbors, normals are inconsistent
  and the orientation test fails → Branch 2 fires → returns false.

Defect pattern: standard tetrahedron with base face wound CW instead of CCW.
  Three lateral faces use CCW winding (normals point outward); the base
  face has its vertex order reversed to CW (normal points inward / upward).
  The mesh is topologically closed (every edge shared by exactly two triangles).
  is_closed passes. PMP.is_outward_oriented fails because the base normal
  is antiparallel to its neighbors at the shared edges → Branch 2 fires.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(0.5,0.5,1)
  CCW lateral faces: (v0,v1,v3), (v1,v2,v3), (v0,v3,v2) — normals outward.
  CW base: (v0,v2,v1) — swapped v1/v2 relative to CCW order (v0,v1,v2);
    normal = (v2-v0)×(v1-v0) = (0.5,1,0)×(1,0,0) = (0,0,-0.5) → -Z (inward).
  Every edge shared by exactly two triangles → closed manifold.
  Euler: V=4, E=6, F=4, chi=2 (sphere / genus-0 closed surface).

Winding check for base (v0,v2,v1):
  e1 = v2 - v0 = (0.5, 1.0, 0.0)
  e2 = v1 - v0 = (1.0, 0.0, 0.0)
  n  = e1 × e2 = (1*0-0*0, 0*1-0.5*0, 0.5*0-1*1) = (0, 0, -1) → -Z (CW winding).
Adjacent lateral t0=(v0,v1,v3):
  e1 = v1 - v0 = (1, 0, 0); e2 = v3 - v0 = (0.5, 0.5, 1)
  n  = (0*1-0*0.5, 0*0.5-1*1, 1*0.5-0*0.5) = (0, -1, 0.5) → points outward (away from interior).
Dot(n_base, n_t0) ∝ (0)*(0) + (0)*(-1) + (-1)*(0.5) = -0.5 < 0 → antiparallel → inconsistent.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me851",
    title="does_bound_a_volume orientation_inconsistent: closed tetrahedron; base wound CW; adjacent normals antiparallel; orientation check fails (Branch 2)",
    defect_class="inconsistent_face_orientation",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — base corner
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — base corner
v2 = m.vertex(0.5, 1.0, 0.0)  # 2 — base corner
v3 = m.vertex(0.5, 0.5, 1.0)  # 3 — apex

# Three lateral faces with CCW winding (normals pointing outward).
t0 = m.triangle(v0, v1, v3)  # 0: front-left; normal outward
t1 = m.triangle(v1, v2, v3)  # 1: front-right; normal outward
t2 = m.triangle(v0, v3, v2)  # 2: back; normal outward

# Base face wound CW — the defect; normal points inward (-Z direction).
t3 = m.triangle(v0, v2, v1)  # 3: base CW (v1 and v2 swapped vs CCW order)

# All edges shared by exactly two triangles → closed manifold.
m.assert_edge_shared(v0, v1, 2)  # t0 and t3
m.assert_edge_shared(v1, v2, 2)  # t1 and t3
m.assert_edge_shared(v0, v2, 2)  # t2 and t3
m.assert_edge_shared(v0, v3, 2)  # t0 and t2
m.assert_edge_shared(v1, v3, 2)  # t0 and t1
m.assert_edge_shared(v2, v3, 2)  # t1 and t2

# Base face (triangle 3) has normal pointing inward (CW winding in XY plane → -Z).
m.assert_triangle_normal_z_negative(3)

# Lateral t0 and base t3 share edge (v0,v1) but normals are antiparallel.
m.assert_adjacent_triangles_inconsistent_winding(t0, t3)

# Euler: V=4, E=6, F=4, chi=2 (closed genus-0 surface = sphere topology).
m.assert_euler_characteristic(4, 6, 4, 2)
