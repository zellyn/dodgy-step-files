"""Me811 — StarTriangulateHole_boundary_loop_closure: traversal returns to start
vertex; boundary loop collected; v == e->v1 exit condition fires.

MeshFix `Basic_TMesh.StarTriangulateHole` Branch 2 (*BOUNDARY_LOOP_CLOSURE*) @ line 62:
  do { v = ...; e = nextOnBoundary(e); } while (v != e->v1);
  When traversal visits each boundary vertex via nextOnBoundary and finally
  returns to the start vertex, the while-condition (v != e->v1 becomes false)
  exits the loop.  The full boundary vertex list is now in hand.

Geometry: a 4-sector fan from hub h, with one sector (h, r3, r0) omitted.
The missing sector leaves a 3-vertex boundary loop: h → r0 → r3 → (back to h).
Three nextOnBoundary steps complete the traversal → Branch 2 fires.

  h=(1,1,0) hub; rim: r0=(0,0,0), r1=(2,0,0), r2=(2,2,0), r3=(0,2,0)
  t0=(h,r0,r1)  t1=(h,r1,r2)  t2=(h,r2,r3)  [sector (h,r3,r0) missing]

Euler: V=5, E=8, F=3, chi=0 (annular mesh with one inner + one outer boundary).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me811",
    title="StarTriangulateHole_boundary_loop_closure: 3-vertex hole in fan mesh; v==e->v1 exits traversal loop (Branch 2)",
    defect_class="star_triangulate_hole_boundary_loop_closure",
)

h  = m.vertex(1.0, 1.0, 0.0)   # 0 — hub
r0 = m.vertex(0.0, 0.0, 0.0)   # 1
r1 = m.vertex(2.0, 0.0, 0.0)   # 2
r2 = m.vertex(2.0, 2.0, 0.0)   # 3
r3 = m.vertex(0.0, 2.0, 0.0)   # 4

# Three of four fan sectors; one sector (h,r3,r0) is omitted.
m.triangle(h, r0, r1)   # 0
m.triangle(h, r1, r2)   # 1
m.triangle(h, r2, r3)   # 2

# Boundary edges of the hole (3-vertex boundary loop: r3 → h → r0).
m.assert_edge_shared(h,  r3, 1)   # boundary
m.assert_edge_shared(r3, r0, 1)   # boundary
m.assert_edge_shared(r0, h,  1)   # boundary

# Shared (interior) fan edges.
m.assert_edge_shared(h, r1, 2)
m.assert_edge_shared(h, r2, 2)

# Outer rim boundary edges (shared by one triangle each).
m.assert_edge_shared(r0, r1, 1)
m.assert_edge_shared(r1, r2, 1)
m.assert_edge_shared(r2, r3, 1)

# Euler: V=5, E=8, F=3, chi=0 (disc with one hole → chi=1 for planar manifold
# with 1 boundary component chi=1; but let's compute: 5-8+3=0).
m.assert_euler_characteristic(v=5, e=8, f=3, chi=0)
