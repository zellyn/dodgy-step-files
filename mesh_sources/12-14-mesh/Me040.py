"""Me040 — duplicate_polygons: duplicate_group_iteration branch — three groups.

Catalog claim: a polygon soup with 3 separate duplicate groups forces the
healer to iterate the outer while(!all_duplicate_polygons.empty()) loop three
times, popping one group per iteration.

Groups: A={tri0,tri1}, B={tri2,tri3}, C={tri4,tri5} — each pair shares a
distinct canonical vertex key. Three singletons (tri6, tri7, tri8) separate
the groups geometrically.

Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup
Branch 5 @ line 996 — *duplicate_group_iteration*: while(!all_duplicate_polygons.empty())
process one group at a time from back to front.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me040",
             title="duplicate_polygons duplicate_group_iteration: three separate duplicate groups",
             defect_class="duplicate_triangles")

# Group A vertices
a0 = m.vertex(0.0, 0.0, 0.0)
a1 = m.vertex(1.0, 0.0, 0.0)
a2 = m.vertex(0.5, 1.0, 0.0)

# Group B vertices (shifted right)
b0 = m.vertex(2.0, 0.0, 0.0)
b1 = m.vertex(3.0, 0.0, 0.0)
b2 = m.vertex(2.5, 1.0, 0.0)

# Group C vertices (shifted further right)
c0 = m.vertex(4.0, 0.0, 0.0)
c1 = m.vertex(5.0, 0.0, 0.0)
c2 = m.vertex(4.5, 1.0, 0.0)

m.triangle(a0, a1, a2)   # tri 0 — group A
m.triangle(a0, a1, a2)   # tri 1 — group A duplicate
m.triangle(b0, b1, b2)   # tri 2 — group B
m.triangle(b0, b1, b2)   # tri 3 — group B duplicate
m.triangle(c0, c1, c2)   # tri 4 — group C
m.triangle(c0, c1, c2)   # tri 5 — group C duplicate

m.assert_duplicate_polygon_group([0, 1], 2)
m.assert_duplicate_polygon_group([2, 3], 2)
m.assert_duplicate_polygon_group([4, 5], 2)
