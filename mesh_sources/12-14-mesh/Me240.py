"""Me240 — negligible_size_area_threshold_default: bbox-diagonal-based default area threshold.

Catalog claim: two disconnected components exist: a large triangulated patch
and a tiny triangle whose area falls below 1% of the bbox-diagonal-squared
default threshold. CGAL PMP.remove_connected_components_of_negligible_size
Branch 1 @ line 180 (*area-threshold-default-inference*) computes
area_threshold = 0.01 * (bbox_diagonal ** 2) when the caller does not supply
an explicit threshold.

Geometric signature: bbox diagonal ≈ sqrt(3) ≈ 1.732; default area threshold
≈ 0.01 * 3.0 = 0.03. The small component triangle has area ≈ 0.00005, which is
far below the default threshold, so it would be removed.

Defect carrier: triangles 0-3 form a unit-cube face patch (component A);
triangle 4 is a microscopic triangle (component B, area ≈ 5e-5), unreachable
from triangle 0 by edge-walk.

Source: CGAL PMP.remove_connected_components_of_negligible_size Branch 1 @
line 180 — *area-threshold-default-inference*: is_default_area_threshold is
true; area_threshold is inferred from bbox_diagonal.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me240",
             title="negligible_size area_threshold_default: tiny component below bbox-derived area threshold",
             defect_class="disconnected_components")

# Component A: a unit-square quad triangulated into 2 triangles (and two extra triangles
# to fill it out), forming a reasonable-sized mesh.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)
# 4 triangles forming the patch (two triangles per quad diagonal split)
t0 = m.triangle(v0, v1, v2)   # face 0: area = 0.5
t1 = m.triangle(v0, v2, v3)   # face 1: area = 0.5
# Add a raised apex for volume.
v4 = m.vertex(0.5, 0.5, 1.0)
t2 = m.triangle(v0, v1, v4)   # face 2
t3 = m.triangle(v1, v2, v4)   # face 3

# Component B: microscopic triangle far from component A.
# Area ≈ 0.5 * 0.01 * 0.01 = 5e-5, well below bbox-diagonal^2 * 0.01 ≈ 0.03
v5 = m.vertex(10.0, 10.0, 0.0)
v6 = m.vertex(10.01, 10.0, 0.0)
v7 = m.vertex(10.0, 10.01, 0.0)
t4 = m.triangle(v5, v6, v7)   # face 4: negligible area component

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t4, t0)

# Assert: the tiny triangle area is well below any reasonable threshold.
m.assert_triangle_area_lt(t4, 1e-3)
