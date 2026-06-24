"""Me1141 — volume_connected_components boundary_component_detection: open mesh with boundary edges; !is_closed flags boundary_error (Branch 2).

CGAL PMP `PMP.volume_connected_components` Branch 2 (*boundary_component_detection*) @ line 600:
  'if(!PMP::is_closed(cc, pmesh))
   { output.boundary_components.push_back(cc); continue; }'
  — after the SI check, each connected component is tested for closure. If any
  boundary edges exist (halfedges with no opposite face), the component is flagged
  as boundary_error and excluded from volume analysis. Only closed components
  proceed to orientation and nesting checks.

Defect pattern: a flat triangulated patch with two triangles sharing one interior
  edge. The four boundary edges (one per outer edge of the two triangles) are each
  incident to only one face — there is no opposite face. The component is connected
  and non-self-intersecting, but !is_closed fires because boundary edges exist.

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0), v3=(3,2,0) — four coplanar vertices.
  t0=(v0,v1,v2): left triangle.
  t1=(v1,v3,v2): right triangle.
  Shared interior edge: (v1,v2) shared by t0 and t1 (2 faces).
  Boundary edges (each incident to 1 face only): (v0,v1), (v0,v2), (v1,v3), (v2,v3).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1141",
    title="volume_connected_components boundary_component_detection: two-triangle flat patch with four boundary edges; !is_closed fires before volume analysis (Branch 2)",
    defect_class="boundary_hole",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left corner
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — bottom center
v2 = m.vertex(1.0, 2.0, 0.0)   # 2 — top left
v3 = m.vertex(3.0, 2.0, 0.0)   # 3 — top right

# Two triangles sharing interior edge (v1,v2).
t0 = m.triangle(v0, v1, v2)   # 0 — left triangle
t1 = m.triangle(v1, v3, v2)   # 1 — right triangle

# Interior edge shared by both triangles (not a boundary edge).
m.assert_edge_shared(v1, v2, 2)

# Boundary edges (each incident to exactly 1 triangle — open mesh).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# The hole boundary loop is the outer perimeter of the two-triangle patch.
m.assert_hole_boundary([v0, v1, v3, v2])

# Euler: V=4, E=5, F=2, chi = 4-5+2 = 1 (open disk, genus 0 with one boundary).
m.assert_euler_characteristic(4, 5, 2, 1)
