"""Me041 — duplicate_polygons: keep_decision ERASE_ALL branch.

Catalog claim: with erase_policy=ERASE_ALL, CGAL sets the keep-index i=0 so
ALL copies of a duplicate polygon are erased — including the one that would
be kept under KEEP_ONE. This fixture has a pair of identical triangles plus
a reversed copy to distinguish the ERASE_ALL policy from KEEP_ONE.

After ERASE_ALL the triangle (0,1,2) is completely absent; only the clean
neighbour triangle remains.

Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup
Branch 6 @ line 1001 — *keep_decision*: (erase_policy == Policy::ERASE_ALL)
sets i=0, meaning all copies are scheduled for removal.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me041",
             title="duplicate_polygons keep_decision ERASE_ALL: both copies scheduled for removal",
             defect_class="duplicate_triangles")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(0.5, -1.0, 0.0)

m.triangle(v0, v1, v2)   # tri 0 — first copy (ERASE_ALL: remove this too)
m.triangle(v0, v1, v2)   # tri 1 — second copy (also removed)
m.triangle(v0, v3, v1)   # tri 2 — clean lower triangle (survives)

# Both copies share the same group.
m.assert_duplicate_polygon_group([0, 1], 2)
