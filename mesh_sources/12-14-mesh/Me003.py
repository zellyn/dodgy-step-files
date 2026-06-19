"""Me003 — near_coincident_vertices: two vertex entries within eps but
not bit-identical.

Catalog claim: vertices 1 and 2 are stored as distinct records with
coordinates separated by 5e-8 (sub-tolerance under any typical CAD
epsilon ~1e-6). Faces reference both as if they were different points,
leaving the mesh as polygon-soup-with-near-duplicates.

Defect carrier: vertex list has two entries for what should be one
point. Healer must snap them together (CGAL snap_vertices /
merge_duplicate_points_in_polygon_soup); failing to do so produces
T-junctions and tiny cracks at the seam.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me003",
             title="near-coincident vertices: 5e-8 separation, distinct entries",
             defect_class="near_coincident_vertices")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.00000005, 0.0, 0.0)   # 5e-8 from v1 — sub-tolerance
v3 = m.vertex(0.5, 1.0, 0.0)

# Two triangles meeting at the near-coincident vertex pair.
m.triangle(v0, v1, v3)   # uses v1
m.triangle(v2, v0, v3)   # uses v2 — should be v1 but isn't

m.assert_vertex_pair_distance_lt(v1, v2, 1e-7)
