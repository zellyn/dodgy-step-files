"""Me1032 — remove_invalid_polygons_erase_execution: polygons.erase(rit, polygons.end()) removes all flagged degenerate faces.

CGAL PMP `PMP.remove_invalid_polygons_in_polygon_soup` Branch 2
(*erase_execution*) @ line 311:
  'polygons.erase(rit, polygons.end());'
  — after std::remove_if moves all invalid polygons to the tail of the
  container, erase() truncates the vector, permanently removing them.
  Branch 2 fires whenever at least one invalid polygon was detected
  (i.e. remove_if returned an iterator before polygons.end()), causing
  the actual container mutation.

Defect pattern: a polygon soup containing two degenerate triangles
  (each with a repeated vertex index) alongside two valid triangles.
  Both degenerate faces are flagged by the Branch 1 predicate and
  moved to the tail by remove_if; Branch 2 then erases them from
  the container. The two valid triangles remain, confirming the
  erase boundary is correct.

Geometry:
  Vertices: v0=(0,0,0), v1=(2,0,0), v2=(1,2,0), v3=(3,0,0).
  Valid triangles:
    t0 = (v0, v1, v2)  — left triangle.
    t1 = (v1, v3, v2)  — right triangle; shares edge (v1,v2) with t0.
  Degenerate triangles (duplicate vertices):
    t2 = (v0, v0, v1)  — zero-area sliver; v0 repeated.
    t3 = (v1, v1, v2)  — zero-area sliver; v1 repeated.
  After erase_execution: only t0 and t1 remain.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1032",
    title="remove_invalid_polygons_erase_execution: two degenerate triangles erased by polygons.erase(rit, end()); two valid triangles remain (Branch 2)",
    defect_class="degenerate_triangle",
)

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(2.0, 0.0, 0.0)
v2 = m.vertex(1.0, 2.0, 0.0)
v3 = m.vertex(3.0, 0.0, 0.0)

# Two valid triangles forming an open fan.
t0 = m.triangle(v0, v1, v2)
t1 = m.triangle(v1, v3, v2)

# Two degenerate triangles with duplicate vertex indices.
t2 = m.triangle(v0, v0, v1)  # v0 repeated — zero-area sliver
t3 = m.triangle(v1, v1, v2)  # v1 repeated — zero-area sliver

# Both degenerate triangles have zero area.
m.assert_triangle_area_lt(t2, 1e-9)
m.assert_triangle_area_lt(t3, 1e-9)

# Outer edges that belong only to valid triangles have correct incidence.
# v0-v2: only in t0 → n=1.
m.assert_edge_shared(v0, v2, 1)
# v1-v3: only in t1 → n=1.
m.assert_edge_shared(v1, v3, 1)
# v2-v3: only in t1 → n=1.
m.assert_edge_shared(v2, v3, 1)
