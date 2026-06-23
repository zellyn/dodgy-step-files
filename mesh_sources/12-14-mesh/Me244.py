"""Me244 — negligible_size_no_criteria: both area and volume thresholds disabled (early return).

Catalog claim: when both area_threshold=0 and volume_threshold=0, neither use_areas
nor use_volumes is set, so CGAL PMP.remove_connected_components_of_negligible_size
Branch 5 @ line 226 (*threshold-criteria-absence*) fires: `if (!use_areas && !use_volumes)`
returns 0 immediately without removing any component.

Geometric signature: the mesh has two disconnected components of vastly different
sizes. However, because both thresholds are zero, NO removal occurs — the branch
catches the vacuous case before any computation.

Defect carrier: a large patch (triangles 0-1) and a tiny triangle (triangle 2).
The disconnection is the defect; the absence-of-criteria branch is what the fixture
exercises.

Source: CGAL PMP.remove_connected_components_of_negligible_size Branch 5 @
line 226 — *threshold-criteria-absence*: `if (!use_areas && !use_volumes) return 0;`
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me244",
             title="negligible_size no_criteria: !use_areas && !use_volumes → early return 0",
             defect_class="disconnected_components")

# Component A: two-triangle patch (total area = 1.0).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)
t0 = m.triangle(v0, v1, v2)   # face 0: area = 0.5
t1 = m.triangle(v0, v2, v3)   # face 1: area = 0.5

# Component B: tiny triangle, distinct location (area ≈ 5e-5).
v4 = m.vertex(50.0, 50.0, 0.0)
v5 = m.vertex(50.01, 50.0, 0.0)
v6 = m.vertex(50.0, 50.01, 0.0)
t2 = m.triangle(v4, v5, v6)   # face 2: negligible size

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t2, t0)

# Assert: the tiny triangle has very small area
# (in the no-criteria scenario, it still wouldn't be removed).
m.assert_triangle_area_lt(t2, 1e-3)
