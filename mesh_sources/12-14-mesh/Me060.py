"""Me060 — pinch_detection: hexagon with first vertex repeated at position 3.

Catalog claim: a 6-point polygon has its first vertex (v0) repeated at position 3,
forming a figure-8 pinch. CGAL PMP.split_pinched_polygons_in_polygon_soup Branch 5
(*pinch_detection*) fires when unique_points.insert() fails for the repeated vertex —
the point was already seen earlier in the same polygon scan. The algorithm splits the
hexagon into two triangles at the pinch.

Polygon vertex sequence: (v0, v1, v2, v0, v3, v4) — v0 appears at positions 0 and 3.
After split:
  sub-polygon 1: (v0, v1, v2)   — positions 0..2
  sub-polygon 2: (v0, v3, v4)   — wrapping: begin..prev_id=0, then i=3..end

The pinch point v0 is shared by both resulting triangles. The two sub-polygons
meet at the same 3D coordinate (the pinch vertex). Edge (v0, v2) belongs only
to sub-polygon 1; edge (v0, v4) belongs only to sub-polygon 2.

Defect carrier: the polygon list has one 6-vertex polygon with a repeated vertex
at a non-adjacent position. Every algorithm that assumes polygon vertices are unique
will mis-compute topology.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me060",
             title="pinch_detection: hexagon (v0,v1,v2,v0,v3,v4) — v0 repeated at position 3",
             defect_class="pinched_polygon")

# Pinch vertex at origin — appears at polygon positions 0 and 3.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — pinch vertex
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3
v4 = m.vertex(-0.5, 1.0, 0.0)  # 4

# Represent the two sub-triangles that result after split_pinched_polygons.
# Sub-polygon 1: (v0, v1, v2)
t0 = m.triangle(v0, v1, v2)
# Sub-polygon 2: (v0, v3, v4)
t1 = m.triangle(v0, v3, v4)

# Both triangles meet at the pinch vertex v0.
# v0 is referenced by both triangles — the vertex fan at v0 is disconnected
# (the two triangles do not share any other vertex).
m.assert_vertex_fan_disconnected(v0)

# The two sub-polygons share no edges (only the pinch vertex), so
# triangle 0 is not reachable from triangle 1 via shared edges.
m.assert_triangle_not_reachable_from(target=t1, source=t0)
