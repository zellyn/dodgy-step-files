"""Me751 — simplify_polygons_in_polygon_soup degenerate_polygon_skip: polygon.size() <= 1 → continue.

CGAL PMP `PMP.simplify_polygons_in_polygon_soup` Branch 2 (*degenerate_polygon_skip*) @ line 168:
  'if(polygon.size() <= 1) continue;' — when a polygon in the soup has 0 or 1 vertex
  (already fully degenerate), the function skips it without calling simplify_polygon().
  This guards against infinite-loop risk in simplify_polygon on minimal input.

Defect pattern: a polygon soup where one entry is a fully-collapsed single-vertex
  polygon: all three stored indices refer to the same vertex v0 (i.e., the soup entry
  is [v0, v0, v0]). After any prior consecutive-duplicate removal pass that reduces
  [v0, v0, v0] → [v0, v0] → [v0], the soup holds a size-1 polygon. The fixture
  represents this state: vertex v0 appears at all three triangle index slots, making
  the polygon a zero-area, single-locus entry. The skip condition fires for this
  polygon so that simplify_polygon() is never called on a size-1 input.

  A second clean triangle (v1, v2, v3) is included so the iteration loop also exercises
  Branch 1 (polygon_iteration) on the non-degenerate polygon.

Geometry:
  v0=(0,0,0) — the degenerate single-point; all indices in t_degenerate reference v0.
  v1=(3,0,0), v2=(4,0,0), v3=(3.5,1,0) — clean triangle vertices.
  t_degenerate = (v0,v0,v0): polygon soup entry [0,0,0] → represents size-1 after collapse.
  t_clean = (v1,v2,v3): polygon soup entry [1,2,3] → distinct consecutive indices.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me751",
    title="simplify_polygons_in_polygon_soup degenerate_polygon_skip: all-same-index triangle (v0,v0,v0) represents size-1 polygon; continue fired (Branch 2)",
    defect_class="degenerate_triangle",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — single-locus degenerate vertex

v1 = m.vertex(3.0, 0.0, 0.0)  # 1 — clean triangle
v2 = m.vertex(4.0, 0.0, 0.0)  # 2
v3 = m.vertex(3.5, 1.0, 0.0)  # 3

# Degenerate soup entry: all three indices identical → size-1 polygon after collapse.
t_degen = m.triangle(v0, v0, v0)   # triangle 0

# Clean triangle: distinct consecutive indices; loop visits but simplify returns 0.
t_clean = m.triangle(v1, v2, v3)   # triangle 1

# Degenerate triangle t_degen has zero area.
m.assert_triangle_area_lt(t_degen, 1e-12)

# Clean triangle boundary edges.
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v1, v3, 1)
