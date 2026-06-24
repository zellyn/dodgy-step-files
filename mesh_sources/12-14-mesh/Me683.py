"""Me683 — holeFilling::TriangulateHole@L98 DELAUNAY_SWAP_IMPROVES_ANGLE: delaunayMinAngle() <= ang; e->swap(1) undone; fast=1 set (Branch 4).

MeshFix `holeFilling::TriangulateHole@L98` Branch 4 (*DELAUNAY_SWAP_IMPROVES_ANGLE*) @ line 145:
  `if (e->delaunayMinAngle() <= ang) { e->swap(1); fast = 1; }`
  — after the hole has been triangulated, the post-fill edge-optimization loop
  sweeps boundary/fill edges checking whether swapping an edge would improve the
  Delaunay min-angle. When delaunayMinAngle() <= ang (the current edge's min
  adjacent angle), swapping improves quality: the swap is performed with fast=1
  (undo flag) to flag that the optimization pass found an improving swap.

Geometry — a small triangular hole with a sub-optimal post-fill triangulation.
The filled mesh has a very flat triangle (needle-like) where swapping the
shared diagonal edge would produce a more equilateral arrangement. The
delaunayMinAngle() for the needle edge is small → <= ang threshold → Branch 4.

Design: a diamond-shaped quadrilateral hole [v0, v1, v2, v3] where v0 and v2
are wide apart but v1 and v3 are close together. A naive fill uses diagonal
(v1,v3). The fill triangle t_fill=(v0,v1,v2) is very flat because v1 and v2
are close and v0 is far. This makes delaunayMinAngle() of edge (v1,v2) small,
triggering the swap.

Vertices:
  v0=(-3,0,0) — far left
  v1=(0,-0.1,0) — slightly below center
  v2=(3,0,0) — far right
  v3=(0,0.1,0) — slightly above center

Hole boundary [v0,v1,v2,v3]: v1 and v3 are nearly coincident (0.2 apart in y).
Frame triangles:
  t0=(v0,v1,v4) — bottom frame (v4=(0,-2,0))
  t1=(v1,v2,v4) — bottom-right frame
  t2=(v2,v3,v5) — top-right frame (v5=(0,2,0))
  t3=(v3,v0,v5) — top-left frame

Interior fill would split along the short diagonal (v1,v3) → very flat triangles
for (v0,v1,v3) and (v1,v2,v3). The edge (v1,v3) has delaunayMinAngle small →
Branch 4 fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me683",
    title="TriangulateHole@L98 DELAUNAY_SWAP_IMPROVES_ANGLE: diamond hole v0-v1-v2-v3; short diagonal (v1,v3) yields needle triangles; delaunayMinAngle()<=ang; swap+fast=1 (Branch 4)",
    defect_class="hole_in_hull",
)

# Hole boundary: wide diamond, v1 and v3 very close vertically.
v0 = m.vertex(-3.0, 0.0, 0.0)   # 0 — far left
v1 = m.vertex( 0.0,-0.1, 0.0)   # 1 — bottom-center (nearly on axis)
v2 = m.vertex( 3.0, 0.0, 0.0)   # 2 — far right
v3 = m.vertex( 0.0, 0.1, 0.0)   # 3 — top-center (nearly on axis)

# Frame vertices.
v4 = m.vertex( 0.0,-2.0, 0.0)   # 4 — far bottom
v5 = m.vertex( 0.0, 2.0, 0.0)   # 5 — far top

# Frame triangles creating the boundary context.
t0 = m.triangle(v0, v1, v4)     # 0 — bottom-left frame
t1 = m.triangle(v1, v2, v4)     # 1 — bottom-right frame
t2 = m.triangle(v2, v3, v5)     # 2 — top-right frame
t3 = m.triangle(v3, v0, v5)     # 3 — top-left frame

# Interior edges shared between frame triangles.
m.assert_edge_shared(v1, v4, 2)  # shared by t0 and t1
m.assert_edge_shared(v3, v5, 2)  # shared by t2 and t3

# Hole boundary: the wide diamond quad [v0, v1, v2, v3].
m.assert_edge_shared(v0, v1, 1)  # hole boundary
m.assert_edge_shared(v1, v2, 1)  # hole boundary
m.assert_edge_shared(v2, v3, 1)  # hole boundary
m.assert_edge_shared(v3, v0, 1)  # hole boundary

m.assert_hole_boundary([v0, v1, v2, v3])

# After hole fill, the naive triangulation splits along short diagonal (v1,v3).
# The two fill triangles (v0,v1,v3) and (v1,v2,v3) are severely needle-shaped:
# v0 and v2 are at x=±3 but v1,v3 are only 0.2 apart in y.
# The interior diagonal edge (v1,v3) has delaunayMinAngle() ≈ small angle,
# and ang (the threshold from the adjacent larger triangle) is larger →
# delaunayMinAngle() <= ang → Branch 4 fires: swap performed, fast=1 set.

# Aspect ratio of the needle fill triangles: longest edge ~3 / shortest alt ~0.1 → ~30.
m.assert_triangle_aspect_ratio_gt(0, 5.0)  # frame triangle t0 is elongated too

# Euler: V=6, E=9, F=4, chi=1 (open disk).
# Edges: (v0,v1),(v1,v4),(v0,v4),(v1,v2),(v2,v4),(v2,v3),(v3,v5),(v2,v5),(v3,v0)
# Wait: t0=(v0,v1,v4): (v0,v1),(v1,v4),(v0,v4)
#       t1=(v1,v2,v4): (v1,v2),(v2,v4),(v1,v4)
#       t2=(v2,v3,v5): (v2,v3),(v3,v5),(v2,v5)
#       t3=(v3,v0,v5): (v3,v0),(v0,v5),(v3,v5)
# Unique edges: (v0,v1),(v0,v4),(v1,v4),(v1,v2),(v2,v4),(v2,v3),(v2,v5),(v3,v5),(v3,v0),(v0,v5)
# = 10 edges, 6 vertices, 4 faces.
# chi = 6 - 10 + 4 = 0. But we have a hole, so chi should be 0 for torus...
# Actually for open disk with one boundary component: chi = 1.
# V=6, E=10, F=4: chi = 6-10+4 = 0. Hmm.
# For open surface with b boundary components: chi = 2 - 2g - b.
# With g=0, b=1: chi = 1. So V - E + F = 1 means E = V + F - 1 = 6 + 4 - 1 = 9.
# I have 10 edges, so chi = 6-10+4 = 0. That means b=2 boundary loops, or genus issue.
# Let me recount: t3 adds edge (v0,v5) which is boundary. (v3,v5) is shared by t2 and t3 → n=2.
# Boundary edges (n=1): (v0,v1),(v1,v2),(v2,v3),(v3,v0) [hole] and
#   (v0,v4),(v2,v4),(v2,v5),(v0,v5) [outer frame boundary].
# Wait that's 8 boundary edges, 2 boundary loops (hole + outer).
# chi = 2 - 2*0 - 2 = 0. So chi=0 is correct!
m.assert_euler_characteristic(6, 10, 4, 0)
