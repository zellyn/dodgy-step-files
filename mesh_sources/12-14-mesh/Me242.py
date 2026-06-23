"""Me242 — negligible_size_area_check: explicit area threshold enables area-based removal.

Catalog claim: two disconnected components exist, with the caller supplying an
explicit area_threshold > 0. CGAL PMP.remove_connected_components_of_negligible_size
Branch 3 @ line 223 (*area-check-applicability*) tests `use_areas` (true when
area_threshold > 0 or default). When use_areas is true, each component's total
area is computed and compared against area_threshold. The tiny component's area
(≈ 0.0005) is below the explicit threshold (e.g. 0.01).

Geometric signature: component A is four triangles forming a patch with total
area ≈ 1.0; component B is a single triangle with area ≈ 0.0005. With
area_threshold=0.01, use_areas=true, and the area check fires (B is below).

Defect carrier: triangles 0-3 form the main patch; triangle 4 is the
negligible component.

Source: CGAL PMP.remove_connected_components_of_negligible_size Branch 3 @
line 223 — *area-check-applicability*: use_areas = (area_threshold > 0); the
branch `if (use_areas)` gates per-component area evaluation.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me242",
             title="negligible_size area_check: use_areas=true; small component below explicit area_threshold",
             defect_class="disconnected_components")

# Component A: two triangles forming a unit square (total area = 1.0).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)
t0 = m.triangle(v0, v1, v2)   # face 0: area = 0.5
t1 = m.triangle(v0, v2, v3)   # face 1: area = 0.5

# Add more faces to make component A clearly dominant.
v4 = m.vertex(2.0, 0.0, 0.0)
v5 = m.vertex(2.0, 1.0, 0.0)
t2 = m.triangle(v1, v4, v5)   # face 2: area = 0.5
t3 = m.triangle(v1, v5, v2)   # face 3: area = 0.5

# Component B: tiny triangle with area = 0.5 * 0.03 * 0.03 = 4.5e-4 < 0.01 threshold.
v6 = m.vertex(10.0, 10.0, 0.0)
v7 = m.vertex(10.03, 10.0, 0.0)
v8 = m.vertex(10.0, 10.03, 0.0)
t4 = m.triangle(v6, v7, v8)   # face 4: area ≈ 4.5e-4

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t4, t0)

# Assert: component B has negligible area (triggers use_areas check).
m.assert_triangle_area_lt(t4, 1e-3)
