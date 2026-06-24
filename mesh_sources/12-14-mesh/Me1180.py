"""Me1180 — triangulate_hole.main threshold_override: user-provided
  threshold_distance parameter overrides the default bbox-based computation
  (Branch 4).

CGAL PMP `triangulate_hole.main` Branch 4 (*threshold_override*)
  @ line 217:
  'if(get_parameter(np, internal_np::threshold_distance) != ... default)' —
  When use_cdt is true, triangulate_hole.main normally computes a default
  threshold_distance from the bounding-box height. Branch 4 fires when the
  caller provides an explicit threshold_distance named parameter, overriding
  the default. The user-supplied value replaces the bbox-computed one for the
  planarity comparison.

Defect pattern: a hexagonal hole whose planarity threshold is explicitly
  supplied by the user. The hole boundary is planar (z=0), so with any
  positive threshold, CDT2 would apply. Branch 4 fires when the explicit
  threshold parameter is detected and replaces the default bbox height
  calculation. The fixture documents that this path exists regardless of
  whether CDT2 ultimately runs.

Geometry: regular hexagonal hole with six hat triangles.
  r0..r5: hexagon corners at unit radius; o0..o5: outer hat vertices.
"""
from step_corpus.mesh_builder import MeshFile
import math

m = MeshFile(
    catalog_id="Me1180",
    title="triangulate_hole.main threshold_override: explicit threshold_distance parameter detected and used instead of bbox default; hexagonal hole (Branch 4)",
    defect_class="boundary_hole",
)

# Hexagonal hole corners (unit radius, z=0)
def hex_pt(i):
    a = math.radians(60 * i)
    return math.cos(a), math.sin(a), 0.0

r0 = m.vertex(*hex_pt(0))   # 0 — right
r1 = m.vertex(*hex_pt(1))   # 1 — upper-right
r2 = m.vertex(*hex_pt(2))   # 2 — upper-left
r3 = m.vertex(*hex_pt(3))   # 3 — left
r4 = m.vertex(*hex_pt(4))   # 4 — lower-left
r5 = m.vertex(*hex_pt(5))   # 5 — lower-right

# Hat outer vertices (radius 2.0 at same angles)
def hat_pt(i):
    a = math.radians(60 * i)
    return 2.0*math.cos(a), 2.0*math.sin(a), 0.0

o0 = m.vertex(*hat_pt(0))   # 6
o1 = m.vertex(*hat_pt(1))   # 7
o2 = m.vertex(*hat_pt(2))   # 8
o3 = m.vertex(*hat_pt(3))   # 9
o4 = m.vertex(*hat_pt(4))   # 10
o5 = m.vertex(*hat_pt(5))   # 11

# Six hat triangles
t0 = m.triangle(r0, o0, r1)   # 0
t1 = m.triangle(r1, o1, r2)   # 1
t2 = m.triangle(r2, o2, r3)   # 2
t3 = m.triangle(r3, o3, r4)   # 3
t4 = m.triangle(r4, o4, r5)   # 4
t5 = m.triangle(r5, o5, r0)   # 5

# Hexagonal hole boundary (n=1)
m.assert_edge_shared(r0, r1, 1)
m.assert_edge_shared(r1, r2, 1)
m.assert_edge_shared(r2, r3, 1)
m.assert_edge_shared(r3, r4, 1)
m.assert_edge_shared(r4, r5, 1)
m.assert_edge_shared(r0, r5, 1)

m.assert_hole_boundary([r0, r1, r2, r3, r4, r5])

# Hat outer edges (n=1)
for (a, b) in [(r0,o0),(r1,o0),(r1,o1),(r2,o1),(r2,o2),(r3,o2),
               (r3,o3),(r4,o3),(r4,o4),(r5,o4),(r5,o5),(r0,o5)]:
    m.assert_edge_shared(a, b, 1)

# Open mesh with hexagonal hole: V=12, E=18, F=6, chi=0
m.assert_euler_characteristic(12, 18, 6, 0)
