"""Me243 — negligible_size_volume_check: explicit volume threshold enables volume-based removal.

Catalog claim: two disconnected closed components exist, with the caller supplying an
explicit volume_threshold > 0. CGAL PMP.remove_connected_components_of_negligible_size
Branch 4 @ line 224 (*volume-check-applicability*) tests `use_volumes` (true when
volume_threshold > 0 or default). When use_volumes is true, each closed component's
volume is computed and compared against volume_threshold.

Geometric signature: component A is a closed tetrahedron (volume ≈ 0.1178);
component B is a tiny closed tetrahedron at (15,15,15) with edge length 0.05
(volume ≈ 1.47e-5, below a threshold of e.g. 1e-3).

Defect carrier: triangles 0-3 form a unit tetrahedron (closed); triangles 4-7
form the micro-tetrahedron (closed), unreachable from triangle 0.

Source: CGAL PMP.remove_connected_components_of_negligible_size Branch 4 @
line 224 — *volume-check-applicability*: use_volumes = (volume_threshold > 0);
the branch `if (use_volumes)` gates per-component volume evaluation.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me243",
             title="negligible_size volume_check: use_volumes=true; tiny closed component below explicit volume_threshold",
             defect_class="disconnected_components")

# Component A: unit tetrahedron (closed, volume ≈ 0.118).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(0.5, 0.333, 0.816)
t0 = m.triangle(v0, v2, v1)   # face 0
t1 = m.triangle(v0, v1, v3)   # face 1
t2 = m.triangle(v1, v2, v3)   # face 2
t3 = m.triangle(v0, v3, v2)   # face 3

# Component B: micro-tetrahedron at (15,15,15) with edge length 0.05.
# Volume ≈ (sqrt(2)/12) * (0.05)^3 ≈ 1.47e-5.
o = [15.0, 15.0, 15.0]
s = 0.05
v4 = m.vertex(o[0],          o[1],          o[2])
v5 = m.vertex(o[0] + s,      o[1],          o[2])
v6 = m.vertex(o[0] + s/2,    o[1] + s,      o[2])
v7 = m.vertex(o[0] + s/2,    o[1] + s/3,    o[2] + s * 0.816)
t4 = m.triangle(v4, v6, v5)   # face 4
t5 = m.triangle(v4, v5, v7)   # face 5
t6 = m.triangle(v5, v6, v7)   # face 6
t7 = m.triangle(v4, v7, v6)   # face 7

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t4, t0)

# Assert the micro-tetrahedron triangles are tiny (triggers use_volumes path).
# Edge length 0.05 → face area ≈ (sqrt(3)/4)*0.05^2 ≈ 0.00108; use 0.005 threshold.
m.assert_triangle_area_lt(t4, 5e-3)
m.assert_triangle_area_lt(t5, 5e-3)
