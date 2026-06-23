"""Me039 — duplicate_polygons: early_exit_empty branch — no duplicates present.

Catalog claim: a clean polygon soup with no duplicate triangles causes the
duplicate collector to find an empty group set. The healer immediately
returns 0 without entering any removal loop.

Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup
Branch 4 @ line 973 — *early_exit_empty*: if(all_duplicate_polygons.empty())
return 0; — fast path when no duplicates exist.

The fixture is a minimal 3-triangle fan where every triangle is distinct.
No duplicate assertions; the oracle run simply confirms 0 assertion failures.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me039",
             title="duplicate_polygons early_exit_empty: all-distinct polygon soup, no duplicates",
             defect_class="duplicate_triangles")

# A clean 4-vertex fan with no repeated faces.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)

m.triangle(v0, v1, v2)   # tri 0
m.triangle(v0, v2, v3)   # tri 1 — different vertex set from tri 0
m.triangle(v1, v3, v2)   # tri 2 — yet another distinct triple

# Edge shared by exactly 2 triangles confirms this is a normal manifold patch,
# not a duplicate-ridden soup.
m.assert_edge_shared(v0, v2, 2)
