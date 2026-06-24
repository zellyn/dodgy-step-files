"""Me681 — holeFilling::TriangulateHole@L98 ANGLE_COMPUTATION_FAILURE: gang == DBL_MAX; all boundary candidates degenerate/collinear; return 0 (Branch 2).

MeshFix `holeFilling::TriangulateHole@L98` Branch 2 (*ANGLE_COMPUTATION_FAILURE*) @ line 122:
  `if (gang == DBL_MAX) { … return 0; }`
  — while scanning boundary candidates, every vertex yields gang == DBL_MAX
  (angle computation fails for all, e.g. near-collinear boundary vertices).
  The algorithm gives up and returns 0 ("Can't complete triangulation").

Geometry — a 4-vertex boundary loop where the four boundary vertices are nearly
collinear in the XY plane. The hole has only one convex position to fill but the
boundary geometry makes angle scoring degenerate.

  Interior context triangles hang off the boundary to make the boundary edges real:
    v0=(0,0,0), v1=(1,0,0), v2=(2,0,0), v3=(3,0,0)  — collinear boundary
    v4=(-1,0,1), v5=(4,0,1)  — far context vertices
  Triangles:
    t0=(v0,v4,v1), t1=(v2,v5,v3)   — left/right context triangles
  This leaves hole boundary edges: (v1,v2) bottom; (v0,v4),(v4,v1) left; (v2,v5),(v5,v3) right.

A simpler design: strip hole with collinear vertices on one side.
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0) — three collinear points
  v3=(1,1,0) — apex forming frame triangles
  Context: two frame triangles share v3.
  t0=(v0,v3,v1), t1=(v1,v3,v2)  — both share interior edge (v1,v3)
  Hole boundary: (v0,v1) n=1, (v1,v2) n=1, (v2,v3) n=1, (v0,v3) n=1

A cleaner collinear-boundary design: open strip where boundary vertices v0,v1,v2
are collinear. The boundary loop [v0,v1,v2,v3] has v0,v1,v2 collinear → angle
at v1 = 180° → gang remains DBL_MAX.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me681",
    title="TriangulateHole@L98 ANGLE_COMPUTATION_FAILURE: gang==DBL_MAX; boundary loop v0-v1-v2 collinear (180° angle); all candidates degenerate; return 0 (Branch 2)",
    defect_class="hole_in_hull",
)

# Boundary loop: v0, v1, v2 are collinear along x-axis; v3 is above.
# This makes the angle at v1 = 180° — degenerate for hole-fill candidate scoring.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left boundary
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — middle boundary (collinear)
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — right boundary (collinear)
v3 = m.vertex(1.0, 2.0, 0.0)   # 3 — top boundary vertex

# Far context vertex to form triangles on the opposite side of the hole.
v4 = m.vertex(1.0, -1.5, 0.0)  # 4 — below the collinear strip

# Frame triangles: surround the hole boundary leaving the quad v0-v1-v2-v3 open.
# Left context: connects v0, v1, v4.
t0 = m.triangle(v0, v1, v4)    # 0 — lower-left frame
# Right context: connects v1, v2, v4.
t1 = m.triangle(v1, v2, v4)    # 1 — lower-right frame
# Upper-left: connects v0, v3.
t2 = m.triangle(v0, v4, v3)    # 2 — far-left frame (spans v0-v4-v3)
# Upper-right: connects v2, v3.
t3 = m.triangle(v2, v3, v4)    # 3 — far-right frame (spans v2-v3-v4)

# Interior edges shared by 2 triangles (frame structure).
m.assert_edge_shared(v1, v4, 2)   # shared between t0 and t1
m.assert_edge_shared(v0, v4, 2)   # shared between t0 and t2
m.assert_edge_shared(v2, v4, 2)   # shared between t1 and t3

# Hole boundary edges: v0-v1, v1-v2 (collinear!) and v0-v3, v2-v3, v3-v4 loops.
m.assert_edge_shared(v0, v1, 1)   # hole boundary — collinear segment
m.assert_edge_shared(v1, v2, 1)   # hole boundary — collinear segment
m.assert_edge_shared(v0, v3, 1)   # hole boundary
m.assert_edge_shared(v2, v3, 1)   # hole boundary

# The hole boundary loop has collinear vertices (v0, v1, v2 along x-axis).
# Angle at v1 = 180° → holeFilling algorithm computes gang = DBL_MAX → Branch 2 fires.
m.assert_hole_boundary([v0, v1, v2, v3])

# Euler: V=5, E=9, F=4, chi=0 (open surface with hole; one boundary component).
m.assert_euler_characteristic(5, 9, 4, 0)
