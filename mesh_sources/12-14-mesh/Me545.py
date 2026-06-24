"""Me545 — checkAndRepair::removeDegenerateTriangles branch 6: UNRESOLVABLE_DEGENERACY

MeshFix `checkAndRepair::removeDegenerateTriangles` Branch 6 (*UNRESOLVABLE_DEGENERACY*) @ line 513:
  'if (t->isExactlyDegenerate()) { ...; degn++; }'
  After all cap-splitting and needle-collapse passes, MeshFix re-checks each triangle
  with isExactlyDegenerate().  A truly degenerate collinear triangle that resists all
  repair strategies increments the degn counter (returned as a negative count), marking
  the mesh as having unresolvable degenerate geometry.

Geometric signature: a triangle whose three vertices are exactly collinear on a line,
  with NO adjacent non-degenerate cap triangle that could provide a split vertex.
  The triangle has zero area and cannot be healed by the cap/needle strategies.

Geometry (z = 0):
  v0=(0,0,0), v1=(4,0,0), v2=(2,0,0)
  All three vertices lie on y=0; triangle is collinear with area=0.
  v3=(2,2,0) — apex of a separate healthy triangle t1 sharing only vertex v2.
  t0 = (v0, v1, v2) — exactly degenerate; all three on y=0; area=0
  t1 = (v0, v2, v3) — healthy; provides mesh context but cannot cure t0
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me545",
    title="checkAndRepair::removeDegenerateTriangles UNRESOLVABLE_DEGENERACY: collinear triangle resists all cap/needle repair; isExactlyDegenerate true after all passes (degn++)",
    defect_class="degenerate_triangle_unresolvable",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left collinear vertex
v1 = m.vertex(4.0, 0.0, 0.0)   # 1 — right collinear vertex
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — middle collinear vertex; lies on v0-v1
v3 = m.vertex(2.0, 2.0, 0.0)   # 3 — healthy apex (context triangle only)

# t0: exactly degenerate — all three vertices collinear on y=0; area=0.
t0 = m.triangle(v0, v1, v2)    # 0 — unresolvable degenerate triangle
# t1: healthy triangle sharing edge (v0, v2) to give mesh context.
t1 = m.triangle(v0, v2, v3)    # 1 — healthy; area=2

# Branch 6 predicate: t0.isExactlyDegenerate() → area=0.
m.assert_triangle_area_lt(0, 1e-9)

# v2 lies on segment v0-v1 (confirming collinearity of t0).
m.assert_vertex_on_edge(v2, v0, v1)

# t1 is healthy; t0 is the unresolvable degenerate.
m.assert_triangle_area_lt(1, 3.0)   # t1 area=2 < 3

# Edge shared by t0 and t1.
m.assert_edge_shared(v0, v2, 2)    # shared between t0 and t1

# t0's other edges are boundary (no adjacent cap that could split it).
m.assert_edge_shared(v0, v1, 1)    # long degenerate edge; boundary only
m.assert_edge_shared(v1, v2, 1)    # boundary only
