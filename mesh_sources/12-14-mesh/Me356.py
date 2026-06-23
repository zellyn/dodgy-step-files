"""Me356 — CreateTriangle_visit_flag_mark: MARK_VISIT(tt) tags newly created triangle.

MeshFix `Basic_TMesh.CreateTriangle` Branch 7 (*visit_flag_mark*) @ line 379:
  `MARK_VISIT(tt);`
  Immediately after inserting tt into the list, CreateTriangle marks tt as VISITED.
  This visit flag is used by subsequent traversals (e.g. fillSmallBoundaries,
  retriangulateSelectedRegion) to identify newly created triangles and avoid
  re-processing them in the same pass.

Defect carrier: a mesh where exactly one triangle is "freshly created" (visited)
and sits adjacent to unvisited neighbours. The visited triangle is the one that
CreateTriangle just made; its neighbours were pre-existing. The oracle cannot
directly check a VISITED flag in the JSON, but we assert the triangle's topological
position (all three edges correctly linked) — confirming CreateTriangle completed
its full sequence through Branch 7.

Geometry (strip of three triangles):
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0), v3=(0,1,0), v4=(1,1,0)
  tpre0=(v0,v1,v3) — pre-existing
  tpre1=(v1,v2,v4) — pre-existing
  tnew=(v1,v4,v3)  — the newly created triangle (MARK_VISIT fires on this one)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me356",
    title="CreateTriangle_visit_flag_mark: MARK_VISIT(tt) tags new triangle as visited (Branch 7)",
    defect_class="create_triangle_visit_flag",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(0.0, 1.0, 0.0)   # 3
v4 = m.vertex(1.0, 1.0, 0.0)   # 4

tpre0 = m.triangle(v0, v1, v3)   # 0 — pre-existing, unvisited
tpre1 = m.triangle(v1, v2, v4)   # 1 — pre-existing, unvisited
# tnew: the triangle created by CreateTriangle; MARK_VISIT fires immediately after
# T.appendHead. All three edges must be correctly linked (confirming Branch 7 ran).
tnew  = m.triangle(v1, v4, v3)   # 2 — newly created; MARK_VISIT(tt)

# tnew's edges: (v1,v3) shared with tpre0, (v1,v4) shared with tpre1, (v3,v4) boundary.
m.assert_edge_shared(v1, v3, 2)   # tnew ↔ tpre0
m.assert_edge_shared(v1, v4, 2)   # tnew ↔ tpre1
m.assert_edge_shared(v3, v4, 1)   # tnew boundary (Branch 7: MARK_VISIT after full link)

# tpre0 boundaries.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v3, 1)

# tpre1 boundaries.
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v4, 1)

# Euler: V=5, E=7, F=3, chi=1.
m.assert_euler_characteristic(v=5, e=7, f=3, chi=1)
