"""Me019 — all SI faces degenerate: faces_to_treat emptiness check.

Catalog claim: the mesh has a region where all triangles involved in the
self-intersection cluster are degenerate (zero area), so after the first
healing pass removes them the face-selection set is empty and the algorithm
must exit the iteration early rather than recompute SI with no candidates.

Source: CGAL PMP.remove_self_intersections Branch 5 @ line 2463 —
*face-selection-emptiness-detection*: whether previous iteration had topology
blockers and no faces remain to process; decides between recomputing SI
or early-loop exit.

Defect carrier: triangles 0 and 2 are valid non-degenerate triangles. Triangles
1 and 3 are zero-area (collinear vertices) degenerate faces that also happen to
have bounding boxes overlapping the valid triangles — they represent the "blocking"
degenerate elements left after a partial heal pass. The zero-area triangles are
the defect; a healer that removes them first empties the faces_to_treat set.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me019",
             title="SI region with degenerate zero-area faces: faces_to_treat empties after removal",
             defect_class="self_intersection_degenerate_cluster")

# Valid triangle 0: in z=0 plane.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
m.triangle(v0, v1, v2)    # tri 0 — valid

# Degenerate triangle 1: all three vertices collinear along X axis (zero area).
v3 = m.vertex(0.2, 0.0, 0.0)   # 3 — on X axis
v4 = m.vertex(0.8, 0.0, 0.0)   # 4 — on X axis (same y, z as v3)
v5 = m.vertex(0.5, 0.0, 0.0)   # 5 — on X axis (between v3 and v4)
m.triangle(v3, v4, v5)    # tri 1 — degenerate: collinear, area=0

# Valid triangle 2: in x=0 plane, perpendicular to tri 0.
v6 = m.vertex(0.0, 0.0,  1.0)  # 6
v7 = m.vertex(0.0, 1.0,  0.0)  # 7
m.triangle(v0, v6, v7)    # tri 2 — valid

# Degenerate triangle 3: three collinear vertices along Z axis.
v8  = m.vertex(0.0, 0.0,  0.2)  # 8
v9  = m.vertex(0.0, 0.0,  0.8)  # 9
v10 = m.vertex(0.0, 0.0,  0.5)  # 10
m.triangle(v8, v9, v10)   # tri 3 — degenerate: collinear, area=0

# Assert: both degenerate triangles have area < 1e-12.
m.assert_triangle_area_lt(1, 1e-12)
m.assert_triangle_area_lt(3, 1e-12)
