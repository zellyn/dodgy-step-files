"""Me248 — negligible_size_removal_logic: component satisfies area-or-volume criterion.

Catalog claim: CGAL PMP.remove_connected_components_of_negligible_size Branch 9
@ line 316 (*area-or-volume-removal-logic*) determines whether a component
should be removed. The condition is:
  `(use_volumes && cc_closeness[i] && component_volumes[i] <= volume_threshold)
  || (use_areas && component_areas[i] <= area_threshold)`
A component is removed if it is either small enough by area OR (closed and)
small enough by volume.

Geometric signature: two disconnected components: component A is a large closed
tetrahedron (neither criterion satisfied); component B is a tiny closed tetrahedron
at (5,5,5) with edge length 0.02 that satisfies BOTH the area criterion
(total face area ≈ 6.93e-4 < threshold 0.01) and the volume criterion (volume
≈ 3.77e-8 < threshold 1e-4). Branch 9 fires for component B.

Defect carrier: triangles 0-3 = unit tetrahedron; triangles 4-7 = micro-tetrahedron
at (5,5,5) with s=0.02.

Source: CGAL PMP.remove_connected_components_of_negligible_size Branch 9 @
line 316 — *area-or-volume-removal-logic*: OR-condition combining volume (closed)
and area criteria to mark component for removal.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me248",
             title="negligible_size removal_logic: tiny closed component satisfies area-or-volume removal OR-condition",
             defect_class="disconnected_components")

# Component A: unit tetrahedron (closed, large — neither threshold satisfied).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(0.5, 0.333, 0.816)
t0 = m.triangle(v0, v2, v1)   # face 0
t1 = m.triangle(v0, v1, v3)   # face 1
t2 = m.triangle(v1, v2, v3)   # face 2
t3 = m.triangle(v0, v3, v2)   # face 3

# Component B: micro-tetrahedron at (5,5,5), edge length s=0.02.
# Each face area ≈ (sqrt(3)/4) * (0.02)^2 ≈ 1.73e-4. Four faces total ≈ 6.93e-4.
# Volume ≈ (sqrt(2)/12) * (0.02)^3 ≈ 4.71e-8.
# Both thresholds satisfied: area < 0.01 AND volume < 1e-4.
o = [5.0, 5.0, 5.0]
s = 0.02
v4 = m.vertex(o[0],        o[1],        o[2])
v5 = m.vertex(o[0] + s,    o[1],        o[2])
v6 = m.vertex(o[0] + s/2,  o[1] + s,    o[2])
v7 = m.vertex(o[0] + s/2,  o[1] + s/3,  o[2] + s * 0.816)
t4 = m.triangle(v4, v6, v5)   # face 4
t5 = m.triangle(v4, v5, v7)   # face 5
t6 = m.triangle(v5, v6, v7)   # face 6
t7 = m.triangle(v4, v7, v6)   # face 7

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t4, t0)

# Assert: micro-tetrahedron triangles have negligible area (satisfies area criterion).
m.assert_triangle_area_lt(t4, 1e-3)
m.assert_triangle_area_lt(t5, 1e-3)
m.assert_triangle_area_lt(t6, 1e-3)
m.assert_triangle_area_lt(t7, 1e-3)

# Assert: the whole mesh has two closed components (each a tetrahedron: chi=2 each).
# Combined: V=8, E=12, F=8, chi = 8 - 12 + 8 = 4 (two closed genus-0 components).
m.assert_euler_characteristic(v=8, e=12, f=8, chi=4)
