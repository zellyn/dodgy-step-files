"""Me542 — checkAndRepair::removeDegenerateTriangles branch 3: SINGLE_CAP_VERTEX

MeshFix `checkAndRepair::removeDegenerateTriangles` Branch 3 (*SINGLE_CAP_VERTEX*) @ line 483:
  'if (nov == 1) splitvs[1] = splitvs[0];'
  When MeshFix searches for cap vertices around a degenerate triangle, it finds
  exactly one unique cap vertex (nov==1).  In this case it duplicates the single
  cap into splitvs[1] so the subsequent split logic can proceed uniformly.

Geometric signature: a degenerate (collinear, zero-area) triangle t0 has only ONE
  adjacent cap triangle sharing a non-degenerate edge.  The other side of the
  degenerate edge is a boundary (no second cap), so nov never increments past 1.

Geometry (z = 0):
  v0=(0,0,0), v1=(4,0,0), v2=(2,0,0)
  t0 = (v0, v1, v2)  — degenerate: collinear, area=0, v2 on v0-v1
  t1 = (v0, v2, v3) where v3=(0,2,0) — single cap triangle on edge (v0,v2)
  Edge (v2,v1) is a boundary (only in t0); only one cap triangle exists → nov==1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me542",
    title="checkAndRepair::removeDegenerateTriangles SINGLE_CAP_VERTEX: nov==1 — only one cap triangle adjacent to degenerate triangle; single cap vertex duplicated",
    defect_class="degenerate_triangle_single_cap_vertex",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left anchor
v1 = m.vertex(4.0, 0.0, 0.0)   # 1 — right anchor
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — midpoint; lies on segment v0-v1
v3 = m.vertex(0.0, 2.0, 0.0)   # 3 — cap apex; only cap triangle present

# t0: exactly degenerate (collinear; area=0).
t0 = m.triangle(v0, v1, v2)    # 0 — degenerate: v2 on v0-v1; area=0
# t1: the single cap triangle; shares edge (v0, v2) with t0.
t1 = m.triangle(v0, v2, v3)    # 1 — healthy cap triangle; area=2

# t0 is exactly degenerate (area < epsilon).
m.assert_triangle_area_lt(0, 1e-9)

# v2 lies strictly inside segment v0-v1 (the degenerate edge).
m.assert_vertex_on_edge(v2, v0, v1)

# Only ONE cap triangle (t1) — nov==1 triggers splitvs[1] = splitvs[0].
# The single shared cap edge is (v0, v2), shared by t0 and t1.
m.assert_edge_shared(v0, v2, 2)    # shared by t0 and t1

# The other edges of t0 are boundary-only (no second cap).
m.assert_edge_shared(v1, v2, 1)    # boundary: only in t0 → no second cap
m.assert_edge_shared(v0, v1, 1)    # boundary: degenerate long edge (only in t0)

# t1 is healthy (area=2 > 0).
m.assert_triangle_area_lt(1, 3.0)
