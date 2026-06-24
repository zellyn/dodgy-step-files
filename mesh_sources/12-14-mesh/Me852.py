"""Me852 — does_bound_a_volume self_intersection: closed mesh with two crossing triangle fans; does_self_intersect returns true; returns false (Branch 3).

CGAL PMP `PMP.does_bound_a_volume` Branch 3 (*self_intersection*) @ line 926:
  'if(PMP::does_self_intersect(tmesh, np)) return false;'
  — after confirming is_closed (Branch 1 passed) and consistent orientation
  (Branch 2 passed), the predicate calls does_self_intersect. If any two
  faces geometrically cross, the mesh cannot bound a valid volume → Branch 3
  fires → returns false.

Defect pattern: two crossing triangle fans (XY-plane fan and XZ-plane fan)
  sharing only a common left apex, embedded in a closed 8-triangle manifold.
  The two fans cross each other along the positive X-axis: t0 (XY-plane) and
  t1 (XZ-plane) share only vertex v0 but their interiors overlap along the
  segment from v0=(0,0,0) to the midpoint (1,0,0). This is a proper
  self-intersection: does_self_intersect returns true → Branch 3 fires.

Geometry (6 vertices, 8 triangles, closed genus-0 manifold):
  v0=(0,0,0)   — shared left apex of both fans
  v1=(2,0,0)   — shared right apex of both fans
  v2=(1, 1,0)  — top-XY (XY fan)
  v3=(1,-1,0)  — bottom-XY (XY fan)
  v4=(1, 0,1)  — top-XZ (XZ fan)
  v5=(1, 0,-1) — bottom-XZ (XZ fan)

  t0=(v0,v2,v3): left XY-plane triangle — normal = (0,0,-1) [CW base]
  t1=(v0,v4,v5): left XZ-plane triangle — crosses t0 along X-axis
  t2=(v1,v3,v2): right XY-plane triangle — closes with t0
  t3=(v1,v5,v4): right XZ-plane triangle — closes with t1
  t4=(v0,v2,v4): top-left connecting cap
  t5=(v1,v4,v2): top-right connecting cap
  t6=(v0,v5,v3): bottom-left connecting cap
  t7=(v1,v3,v5): bottom-right connecting cap

  Self-intersection: t0 (z=0 plane, y in [-1,1]) and t1 (y=0 plane, z in [-1,1])
  share only v0 but their interiors overlap along the segment
  from (0,0,0) to (1,0,0) — the positive X half-axis.

Edge count: 12 distinct edges, each shared by exactly 2 triangles.
  Euler: V=6, E=12, F=8, chi=2 (genus-0 closed surface).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me852",
    title="does_bound_a_volume self_intersection: XY/XZ crossing fans in closed 8-tri manifold; interior overlap along X-axis; does_self_intersect true (Branch 3)",
    defect_class="self_intersection",
)

v0 = m.vertex(0.0, 0.0,  0.0)  # 0 — left apex (shared by both fans)
v1 = m.vertex(2.0, 0.0,  0.0)  # 1 — right apex (shared by both fans)
v2 = m.vertex(1.0, 1.0,  0.0)  # 2 — XY fan top
v3 = m.vertex(1.0,-1.0,  0.0)  # 3 — XY fan bottom
v4 = m.vertex(1.0, 0.0,  1.0)  # 4 — XZ fan top
v5 = m.vertex(1.0, 0.0, -1.0)  # 5 — XZ fan bottom

# Two crossing fans — the self-intersecting core.
t0 = m.triangle(v0, v2, v3)   # 0: left XY-plane fan
t1 = m.triangle(v0, v4, v5)   # 1: left XZ-plane fan; crosses t0 along X-axis

# Right-side mirror triangles.
t2 = m.triangle(v1, v3, v2)   # 2: right XY fan (pairs edges (v2,v3) with t0)
t3 = m.triangle(v1, v5, v4)   # 3: right XZ fan (pairs edges (v4,v5) with t1)

# Connecting caps (close the four longitudinal seams).
t4 = m.triangle(v0, v2, v4)   # 4: top-left cap
t5 = m.triangle(v1, v4, v2)   # 5: top-right cap  (pairs (v2,v4) with t4)
t6 = m.triangle(v0, v5, v3)   # 6: bottom-left cap
t7 = m.triangle(v1, v3, v5)   # 7: bottom-right cap (pairs (v3,v5) with t6)

# All 12 edges shared by exactly 2 triangles — closed manifold.
m.assert_edge_shared(v2, v3, 2)  # t0 + t2
m.assert_edge_shared(v4, v5, 2)  # t1 + t3
m.assert_edge_shared(v0, v2, 2)  # t0 + t4
m.assert_edge_shared(v0, v4, 2)  # t1 + t4
m.assert_edge_shared(v2, v4, 2)  # t4 + t5
m.assert_edge_shared(v1, v4, 2)  # t3 + t5
m.assert_edge_shared(v1, v2, 2)  # t2 + t5
m.assert_edge_shared(v0, v5, 2)  # t1 + t6
m.assert_edge_shared(v0, v3, 2)  # t0 + t6
m.assert_edge_shared(v3, v5, 2)  # t6 + t7
m.assert_edge_shared(v1, v3, 2)  # t2 + t7
m.assert_edge_shared(v1, v5, 2)  # t3 + t7

# Self-intersecting pair: t0 and t1 share only v0; interiors overlap along
# the positive X half-axis from (0,0,0) to (1,0,0).
m.assert_triangles_self_intersect(t0, t1)

# Euler: V=6, E=12, F=8, chi=2 (closed genus-0 surface).
m.assert_euler_characteristic(6, 12, 8, 2)
