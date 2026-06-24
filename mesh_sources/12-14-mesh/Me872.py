"""Me872 — selectIntersectingTriangles spatial recursion vs termination:
fork() subdivides cells deeper vs todo.appendTail queues for intersection test (Branch 3).

MeshFix `Basic_TMesh.selectIntersectingTriangles` Branch 3 (*Spatial recursion vs termination*) @ line 172:
  'if (condition) { fork(); } else { todo.appendTail(cell); }' — the partitioner
  either recurses deeper by splitting a cell at its midpoint (fork()), or decides
  the cell is small enough and appends it to the todo queue for triangle-pair
  intersection testing (todo.appendTail). Branch 3 is the decision point that
  controls whether recursion continues or terminates for each cell.

This fixture presents a pair of self-intersecting triangles within a bounding
region designed to require multiple spatial subdivision levels before the cells
become small enough to terminate recursion (fork() fires at the outer level,
then todo.appendTail fires when a leaf cell is reached). The geometry creates
a crossing pair that survives multiple rounds of the fork/append decision before
the intersection is detected.

Defect pattern: 'fork()', 'todo.appendTail' — spatial recursion splits at
  midpoint at each level until cells are small enough to queue for SI testing.

Geometry:
  Two crossing triangles in a moderate bounding region (3x3 unit box):
    t0 (XY plane, diagonal): (0,0,0), (3,3,0), (3,0,0)
    t1 (XZ plane, crossing): (0,0,0), (3,0,3), (3,0,-1)
  They share the apex (0,0,0) and cross along the X-axis direction.
  Six surrounding triangles fill the scene to exercise the cell-traversal
  recursion tree (fork fires on outer cells; appendTail fires on leaf cells
  that contain the crossing pair).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me872",
    title="selectIntersectingTriangles spatial-recursion vs termination: fork() at outer cells then todo.appendTail at leaf cell containing SI pair (Branch 3)",
    defect_class="self_intersection_face_pair",
)

# Core crossing pair — share apex at origin, cross along X-axis.
v0 = m.vertex(0.0, 0.0,  0.0)   # 0 — shared apex
v1 = m.vertex(3.0, 3.0,  0.0)   # 1 — XY slab
v2 = m.vertex(3.0, 0.0,  0.0)   # 2 — XY slab (on X axis)
v3 = m.vertex(3.0, 0.0,  3.0)   # 3 — XZ slab
v4 = m.vertex(3.0, 0.0, -1.0)   # 4 — XZ slab

t0 = m.triangle(v0, v1, v2)     # 0: XY-plane diagonal triangle
t1 = m.triangle(v0, v3, v4)     # 1: XZ-plane triangle; crosses t0 along X-axis

# Surrounding triangles to populate outer spatial cells (fork fires on these).
# Placed in spatially distinct quadrants to create a non-trivial partition tree.
v5  = m.vertex(-3.0, -3.0, 0.0)   # 5
v6  = m.vertex(-1.0, -3.0, 0.0)   # 6
v7  = m.vertex(-3.0, -1.0, 0.0)   # 7

v8  = m.vertex(5.0, -3.0, 0.0)    # 8
v9  = m.vertex(7.0, -3.0, 0.0)    # 9
v10 = m.vertex(5.0, -1.0, 0.0)    # 10

v11 = m.vertex(-3.0, 5.0, 0.0)    # 11
v12 = m.vertex(-1.0, 5.0, 0.0)    # 12
v13 = m.vertex(-3.0, 7.0, 0.0)    # 13

v14 = m.vertex(5.0, 5.0,  2.0)    # 14
v15 = m.vertex(7.0, 5.0,  2.0)    # 15
v16 = m.vertex(5.0, 7.0,  2.0)    # 16

t2 = m.triangle(v5,  v6,  v7)     # 2: lower-left quadrant — outer cell
t3 = m.triangle(v8,  v9,  v10)    # 3: lower-right quadrant — outer cell
t4 = m.triangle(v11, v12, v13)    # 4: upper-left quadrant — outer cell
t5 = m.triangle(v14, v15, v16)    # 5: upper-right quadrant — outer cell (in Z)

# Two more triangles adjacent to the crossing pair to deepen the recursion tree.
v17 = m.vertex(1.5, 1.5,  0.0)    # 17
v18 = m.vertex(2.5, 0.5,  0.0)    # 18
v19 = m.vertex(1.5, 0.5,  1.5)    # 19
v20 = m.vertex(2.5, 0.5,  1.5)    # 20

t6 = m.triangle(v17, v18, v2)     # 6: near core — triggers fork then appendTail
t7 = m.triangle(v19, v20, v3)     # 7: near core — triggers fork then appendTail

# The core crossing pair is the SI defect.
m.assert_triangles_self_intersect(t0, t1)

# Outer quadrant triangles are spatially separated — leaf cells that appendTail
# but find no intersection on testing.
m.assert_triangles_do_not_intersect(t2, t3)
m.assert_triangles_do_not_intersect(t4, t5)
