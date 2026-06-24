"""Me475 — remove_a_border_edge hk2_equals_hp: degenerate fan where hk2==hp (Branch 6).

CGAL PMP `PMP.remove_a_border_edge.with_sets` Branch 6 (*halfedge_identity_match*) @ line 1348:
  'hk2 == hp' — the halfedge hk2 (obtained by walking around the region boundary)
  equals hp (the halfedge at the collapse target); different pointer restoration path.

In the normal collapse path, hk2 and hp are distinct halfedges pointing to different
vertices. But in a degenerate fan — where the region has only ONE triangle and that
triangle's boundary halfedges close up on themselves — hk2 and hp can coincide.
This happens when the region to remove is a single triangle with exactly two border
edges, and the vertex fan around the collapse point has minimal size (degree 2 at
the border vertex), so the next halfedge in the traversal wraps all the way back to
the starting halfedge.

Geometry: a 2-triangle fan sharing a single apex vertex where the region triangle
has only one interior neighbor. The apex vertex has degree 2 in the fan, so
traversing the halfedges: h → hk1 → hk2 wraps to hp.

  v0=(0,0,0) — apex (degree-2 border vertex)
  v1=(1,0,0) — right base
  v2=(0,1,0) — top (interior-edge neighbor)
  v3=(-1,0,0) — left base

  t0=(v0,v1,v2) — right triangle: border edge (v0,v1), interior edge (v0,v2)
  t1=(v0,v2,v3) — left triangle: border edge (v0,v3), interior edge (v0,v2)

  Interior edge (v0,v2) shared by t0 and t1 — n=2.
  Both triangles share apex v0 at degree 2 in the fan (only two triangles around v0).
  When the algorithm processes border edge (v0,v1):
    h points along (v0→v1)
    hp = opposite(next(h)) points around the region
    hk1 = next(h) in t0
    hk2 = next halfedge after hk1 around v0's fan = the halfedge in t1
    Since v0 has degree exactly 2, hk2 wraps back to hp → hk2 == hp triggers Branch 6.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me475",
    title="remove_a_border_edge hk2_equals_hp: degree-2 apex v0 in 2-triangle fan; hk2 wraps to hp (Branch 6)",
    defect_class="border_edge_hk2_equals_hp",
)

# Degree-2 fan apex: only two triangles meet at v0.
v0 = m.vertex(0.0,  0.0, 0.0)   # 0 — apex, degree 2; the degenerate fan center
v1 = m.vertex(1.0,  0.0, 0.0)   # 1 — right base endpoint
v2 = m.vertex(0.0,  1.0, 0.0)   # 2 — top vertex (interior edge endpoint)
v3 = m.vertex(-1.0, 0.0, 0.0)   # 3 — left base endpoint

t0 = m.triangle(v0, v1, v2)   # 0: right triangle; border (v0,v1), interior (v0,v2)
t1 = m.triangle(v0, v2, v3)   # 1: left triangle;  border (v0,v3), interior (v0,v2)

# Interior shared edge (v0,v2) — n=2; links the two triangles in the fan.
m.assert_edge_shared(v0, v2, 2)

# Border edges — n=1 each.
m.assert_edge_shared(v0, v1, 1)   # border edge on right
m.assert_edge_shared(v0, v3, 1)   # border edge on left
m.assert_edge_shared(v1, v2, 1)   # far border edge of right triangle
m.assert_edge_shared(v2, v3, 1)   # far border edge of left triangle

# The outer boundary loop: v0→v1→v2→v3→v0.
m.assert_hole_boundary([v0, v1, v2, v3])

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
