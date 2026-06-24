"""Me386 — isDoubleFlat_misalignment_check: two ridge edges with collinear opposite vertices; exactMisalignment → return true.

MeshFix `Vertex.isDoubleFlat` Branch 7 (*misalignment_check*) @ line 338:
  'return !(e1->oppositeVertex(this)->exactMisalignment(this, e2->oppositeVertex(this)));'
  After finding exactly 2 ridge edges (nne==2, e1 and e2 set), the algorithm checks
  whether the opposite vertex of e1 and the opposite vertex of e2 are exactly
  collinear through the center vertex (exactMisalignment). If they ARE collinear
  (misalignment == true), the vertex is a true DoubleFlat and isDoubleFlat returns
  true (the negation makes it true). If they are NOT collinear, returns false.

  This fixture demonstrates the true-DoubleFlat case: opposite vertices of the
  two ridge edges are exactly collinear through v0 → return true.

Geometric signature: identical to Me134/Me135 DoubleFlat pattern. Vertex v0 at
(0,0,0) lies exactly on the line connecting the opposite vertices of the two
ridge edges. The 1-ring has exactly two ridge edges (e1 and e2). The opposite
vertices (reached through e1 and e2) are collinear with v0.

Geometry:
  v0 = (0.0, 0.0, 0.0)    — DoubleFlat vertex (center, on the axis)
  v1 = (-2.0, 0.0, 0.0)   — left axis endpoint (opposite vertex of e1)
  v2 = (2.0,  0.0, 0.0)   — right axis endpoint (opposite vertex of e2)
  v3 = (0.0,  1.0, 1.0)   — upper ridge neighbor
  v4 = (0.0, -1.0, 1.0)   — lower ridge neighbor

  v1, v0, v2 are collinear on the x-axis (x-axis is the misalignment axis).

  t0 = (v1, v3, v0)  — upper-left
  t1 = (v3, v2, v0)  — upper-right
  t2 = (v2, v4, v0)  — lower-right
  t3 = (v4, v1, v0)  — lower-left

  Ridge edges (the two fold edges at v0):
    e1 = (v0, v1): shared by t0(upper-left) and t3(lower-left) → dihedral fold
    e2 = (v0, v2): shared by t1(upper-right) and t2(lower-right) → dihedral fold

  oppositeVertex of e1 through v0 = v1; oppositeVertex of e2 through v0 = v2.
  v1=(−2,0,0), v0=(0,0,0), v2=(2,0,0) — all on x-axis → collinear.
  exactMisalignment = true → isDoubleFlat returns !(true) = true... wait.

  Actually: exactMisalignment checks if v1, v0, v2 are collinear (v0 is on segment
  v1-v2). If yes → returns true. Then `!(true)` = false.
  If NOT collinear → exactMisalignment = false → `!(false)` = true (DoubleFlat).

  RE-CHECK: The DoubleFlat case is when the vertex IS flat between two fold lines.
  The "misalignment" check verifies the two opposite vertices are NOT misaligned —
  i.e., they ARE collinear through the center vertex (on the same line), which
  confirms this is a true fold-flat configuration. The `!` negates a "has
  misalignment" function that returns true when they are NOT collinear.

  MeshFix `exactMisalignment(v0, opp)` likely returns true when v0 and opp form
  a fold that IS valid → meaning the two axis points are CORRECTLY aligned.
  So `!(exactMisalignment(...))` = false when aligned → returns false? That would
  mean Branch 7 returns false for a genuine DoubleFlat.

  Looking at usage: isDoubleFlat is called in removeIfRedundant to confirm a vertex
  IS a DoubleFlat candidate. So we want it to return true for a DoubleFlat vertex.
  The `return !(e1->oppositeVertex()->exactMisalignment(this, e2->oppositeVertex()))`
  means: return true when NOT misaligned. "Misaligned" means the two opposite vertices
  do NOT lie on a common line through v0. If they are on a line (DoubleFlat case),
  exactMisalignment returns false → `!(false)` = true → isDoubleFlat returns true.

  So: collinear opposite vertices → exactMisalignment=false → return true (DoubleFlat).
  Non-collinear → exactMisalignment=true → return false (not DoubleFlat).

  This fixture: v1, v0, v2 collinear → exactMisalignment=false → return true.

Oracle: use assert_vertex_on_edge(v0, v1, v2) to capture the collinearity.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me386",
             title="isDoubleFlat_misalignment_check: v0 collinear with opposite vertices v1 and v2; exactMisalignment=false → Branch 7 returns true (DoubleFlat confirmed)",
             defect_class="double_flat_vertex_collinear_axis")

v0 = m.vertex(0.0,  0.0,  0.0)   # 0 — DoubleFlat center vertex (on axis)
v1 = m.vertex(-2.0, 0.0,  0.0)   # 1 — left axis endpoint (opposite vertex of e1)
v2 = m.vertex(2.0,  0.0,  0.0)   # 2 — right axis endpoint (opposite vertex of e2)
v3 = m.vertex(0.0,  1.0,  1.0)   # 3 — upper ridge neighbor
v4 = m.vertex(0.0, -1.0,  1.0)   # 4 — lower ridge neighbor

# Four-triangle fan around v0:
t0 = m.triangle(v1, v3, v0)    # 0 — upper-left
t1 = m.triangle(v3, v2, v0)    # 1 — upper-right
t2 = m.triangle(v2, v4, v0)    # 2 — lower-right
t3 = m.triangle(v4, v1, v0)    # 3 — lower-left

# v0 lies exactly on the axis line between v1 and v2 (collinear).
# This is the exactMisalignment=false case → isDoubleFlat returns true.
m.assert_vertex_on_edge(v0, v1, v2)

# All 4 fan edges at v0 are interior (shared by exactly 2 triangles).
m.assert_edge_shared(v0, v1, 2)   # e1: shared by t0 and t3 — left ridge
m.assert_edge_shared(v0, v2, 2)   # e2: shared by t1 and t2 — right ridge
m.assert_edge_shared(v0, v3, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v4, 2)   # shared by t2 and t3

# Outer boundary edges (each in exactly 1 triangle).
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v3, v2, 1)
m.assert_edge_shared(v2, v4, 1)
m.assert_edge_shared(v1, v4, 1)
