"""Me470 — remove_a_border_edge link_condition_satisfied: border edge collapses safely (Branch 1).

CGAL PMP `PMP.remove_a_border_edge.with_sets` Branch 1 (*link_condition_satisfied*) @ line 1193:
  'does_satisfy_link_condition(halfedge, tmesh)' → true; proceed with collapse_edge.

The link condition for collapsing edge (v0,v1) requires that the set of common
neighbors of v0 and v1 equals exactly the set of triangles incident to both.
In a minimal 2-triangle border patch the condition is satisfied: v0 and v1 each
have exactly one common neighbor (the shared vertex v2 on the interior), and no
T-junction fans exist that would create multiple common neighbors.

Geometry: three triangles arranged around a central border edge (v0,v1).
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(0.5,-1,0)
  t0=(v0,v2,v1) — upper triangle
  t1=(v0,v1,v3) — lower triangle
  t2=(v0,v3,v2)? No — keep it simple: just 2 triangles sharing the interior edge.

Minimal fixture: two triangles sharing interior edge (v0,v2), with border edge (v0,v1).
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(-0.5,1,0)
  t0=(v0,v1,v2) — right triangle; border edge (v1,v2) and (v0,v1)
  t1=(v0,v2,v3) — left triangle; border edge (v0,v3) and (v3,v2)
  Shared interior edge: (v0,v2) — n=2
  Border edge to collapse: (v0,v1) — n=1; link condition satisfied since
  link(v0) ∩ link(v1) = {v2} which matches the triangles incident to both v0 and v1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me470",
    title="remove_a_border_edge link_condition_satisfied: border edge (v0,v1) collapses safely; 2-triangle open strip (Branch 1)",
    defect_class="border_edge_link_condition_satisfied",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left endpoint of border edge
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — right endpoint of border edge
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — shared apex (interior to both triangles)
v3 = m.vertex(-0.5, 1.0, 0.0)  # 3 — far-left apex (exterior to shared edge)

# Two triangles sharing interior edge (v0, v2).
t0 = m.triangle(v0, v1, v2)   # 0: right triangle — contains border edge (v0,v1)
t1 = m.triangle(v0, v2, v3)   # 1: left triangle — no shared vertex with v1

# Interior shared edge (v0, v2) — n=2.
# The link condition on border edge (v0,v1): link(v0)∩link(v1) = {v2};
# both v0 and v1 are connected to v2 only via t0, so the link condition is satisfied.
m.assert_edge_shared(v0, v2, 2)

# Border edges — n=1 each (boundary of the open strip).
m.assert_edge_shared(v0, v1, 1)   # border edge to be collapsed
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Euler: V=4, E=5, F=2, chi=1 (open surface with one boundary loop).
m.assert_euler_characteristic(4, 5, 2, 1)
