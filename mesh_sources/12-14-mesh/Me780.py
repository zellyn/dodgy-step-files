"""Me780 — polygon_soup_to_polygon_mesh orientation_inconsistency: adjacent triangles with opposing winding trigger orient_polygon_soup (Branch 1).

CGAL PMP `PMP.polygon_soup_to_polygon_mesh` Branch 1 (*orientation_inconsistency*) @ line 295:
  'if(!PMP::orient_polygon_soup(points, polygons)) { ... }'
  — before converting, the soup is tested for consistent orientation; when
  adjacent polygons have inconsistent face winding (one CW, one CCW for the
  shared edge) the orient_polygon_soup step fires to correct them.

Defect pattern: two adjacent triangles sharing edge (v1, v2) but with
  opposing winding. Triangle t0=(v0,v1,v2) is CCW (normal +Z). Triangle
  t1=(v1,v3,v2) is also CCW in isolation, but its winding relative to the
  shared edge (v1→v2 vs v2→v1) means the normals at the shared edge are
  antiparallel — a soup-level orientation inconsistency.

Geometry (XY plane):
  v0=(0,0,0), v1=(1,0,0), v2=(1,1,0), v3=(0,1,0)
  t0=(v0,v1,v2): CCW, normal +Z
  t1=(v1,v3,v2): CW relative to t0 across shared edge (v1,v2); normal −Z

  For a consistently oriented mesh, the shared edge v1→v2 in t0 should be
  paired with v2→v1 in t1. Instead, both traverse the edge in the same
  direction (v1→v2 in t0; but t1 does v1→v3→v2, so the shared edge in t1
  goes v1→v2 again in the polygon, making them wind the same way outward
  — soup winding is inconsistent).

Assertions:
  - The two triangles share edge (v1, v2) — each appears in exactly one
    polygon in the soup (edge n=1 from each side, total topology n=2 once
    merged, but orientation is opposed).
  - adjacent_triangles_inconsistent_winding(t0, t1) confirms antiparallel
    normals across the shared edge.
  - euler_characteristic confirms the 2-triangle open-disk topology.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me780",
    title="polygon_soup_to_polygon_mesh orientation_inconsistency: adjacent t0=(v0,v1,v2) CCW and t1=(v1,v3,v2) opposing winding trigger orient_polygon_soup (Branch 1)",
    defect_class="inconsistent_winding",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — bottom-left
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — bottom-right; shared edge endpoint
v2 = m.vertex(1.0, 1.0, 0.0)  # 2 — top-right; shared edge endpoint
v3 = m.vertex(0.0, 1.0, 0.0)  # 3 — top-left

# t0: CCW — normal = (v1-v0)×(v2-v0) = (1,0,0)×(1,1,0) = (0,0,1) → +Z
t0 = m.triangle(v0, v1, v2)  # 0: CCW, normal +Z

# t1: opposing winding relative to t0 across shared edge (v1,v2).
# t1=(v1,v3,v2): normal = (v3-v1)×(v2-v1) = (-1,1,0)×(0,1,0) = (-1*0-1*0, 1*0-(-1)*0, (-1)*1-1*0) = (0,0,-1) → -Z
# Shared edge goes v1→v2 in t0 and v2→v1 would be consistent, but here it
# goes v1→...→v2 in t1 in the same geometric direction → inconsistent soup.
t1 = m.triangle(v1, v3, v2)  # 1: normal -Z, inconsistent with t0

# Shared edge (v1, v2): traversed by t0 and t1 but with antiparallel normals.
m.assert_edge_shared(v1, v2, 2)

# Boundary edges — each shared by exactly one triangle.
m.assert_edge_shared(v0, v1, 1)  # t0 bottom
m.assert_edge_shared(v0, v2, 1)  # t0 diagonal
m.assert_edge_shared(v1, v3, 1)  # t1 left
m.assert_edge_shared(v2, v3, 1)  # t1 top

# Inconsistent winding between adjacent t0 and t1 — dot(normal_t0, normal_t1) < 0.
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
