"""Me241 — negligible_size_volume_threshold_default: bbox-diagonal-based default volume threshold.

Catalog claim: two disconnected components exist: a closed tetrahedral shell
and a tiny closed component whose volume falls below 1% of the
bbox-diagonal-cubed default threshold. CGAL PMP.remove_connected_components_of_negligible_size
Branch 2 @ line 181 (*volume-threshold-default-inference*) computes
volume_threshold = 0.01 * (bbox_diagonal ** 3) when the caller does not supply
an explicit volume threshold.

Geometric signature: the large component is a closed tetrahedron (V=4, E=6, F=4,
chi=2). The small component is a micro-tetrahedron with edge length 0.001, volume
≈ 1.18e-10, far below any plausible default threshold.

Defect carrier: triangles 0-3 form a unit tetrahedron (component A, closed);
triangles 4-7 form a micro-tetrahedron at (20,20,20) (component B, closed),
unreachable from triangle 0.

Source: CGAL PMP.remove_connected_components_of_negligible_size Branch 2 @
line 181 — *volume-threshold-default-inference*: is_default_volume_threshold is
true; volume_threshold is inferred from bbox_diagonal.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me241",
             title="negligible_size volume_threshold_default: tiny closed component below bbox-derived volume threshold",
             defect_class="disconnected_components")

# Component A: unit tetrahedron (closed, volume = sqrt(2)/12 ≈ 0.1178).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(0.5, 0.333, 0.816)
t0 = m.triangle(v0, v2, v1)   # face 0 (CCW from outside)
t1 = m.triangle(v0, v1, v3)   # face 1
t2 = m.triangle(v1, v2, v3)   # face 2
t3 = m.triangle(v0, v3, v2)   # face 3

# Component B: micro-tetrahedron at (20,20,20), edge length = 0.001.
# Volume ≈ (sqrt(2)/12) * (0.001)^3 ≈ 1.18e-10.
o = [20.0, 20.0, 20.0]
s = 0.001
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

# Assert the micro-tetrahedron triangles have very small area.
m.assert_triangle_area_lt(t4, 1e-6)
m.assert_triangle_area_lt(t5, 1e-6)
