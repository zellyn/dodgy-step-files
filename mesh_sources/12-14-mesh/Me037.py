"""Me037 — duplicate_polygons: orientation_requirement branch — reversed polygon.

Catalog claim: triangle 0 is (0,1,2) and triangle 1 is (0,2,1) — identical
vertex sets but opposite winding. With require_same_orientation=true the healer
does NOT classify these as duplicates; with require_same_orientation=false it
does. The fixture embeds the reversed pair so a healer must consult its
orientation flag before deciding.

Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup
Branch 2 @ line 955 — *orientation_requirement*: require_same_orientation NP
controls whether winding-reversed copies are treated as duplicates.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me037",
             title="duplicate_polygons orientation_requirement: reversed-winding pair",
             defect_class="duplicate_triangles")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(0.5, -1.0, 0.0)

m.triangle(v0, v1, v2)   # tri 0 — CCW (outward in z=0 upper half)
m.triangle(v0, v2, v1)   # tri 1 — CW  (reversed winding, same vertices)
m.triangle(v0, v3, v1)   # tri 2 — clean lower triangle

# Tri 0 and tri 1 have the same vertex set but opposite winding.
m.assert_reversed_polygon_pair(0, 1)
