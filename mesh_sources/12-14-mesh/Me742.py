"""Me742 — TriangulateHole_L439_angle_computation_failure: collinear hole boundary; gang == DBL_MAX; unmark vertices and unlink triangles; return 0 (Branch 3).

MeshFix `holeFilling::TriangulateHole` Branch 3 (*ANGLE_COMPUTATION_FAILURE*) @ line 467:
  'if (gang == DBL_MAX) { ... unmark; unlink; return 0; }'
  While iterating the hole boundary to find the vertex with the smallest
  internal angle, the algorithm accumulates a minimum angle `gang`. If no valid
  angle can be computed — because all candidate vertices are collinear or
  geometrically degenerate — gang remains at DBL_MAX. Branch 3 cleans up and
  returns 0.

Defect pattern: a hole whose boundary vertices are all collinear (all on the
  X-axis). The internal angle at every vertex is either 0° or 180°, making it
  impossible to identify a valid triangulation apex. The healer sets gang=DBL_MAX
  and never finds a vertex with a finite angle → Branch 3 fires.

Geometry:
  Three collinear hole-rim vertices: h0=(0,0,0), h1=(1,0,0), h2=(2,0,0).
  Two frame triangles bridge the hole with off-axis apex vertices.
  fa=(1,1,0) connects h0, h1, h2 as two triangles above the hole.
  fb=(1,-1,0) connects h0, h1, h2 as two triangles below the hole.

  Hole boundary loop: h0→h1 (above-only), h1→h2 (above-only), h2→h0 (bridge).
  Actually: the top fan closes the top; we need an open hole.

  Simplified: three collinear hole verts with frame triangles left+right.
    Left triangle t0=(h0, h1, fl) where fl=(0.5, 1,0)
    Right triangle t1=(h1, h2, fr) where fr=(1.5, 1,0)
    Bottom bridge t2=(h2, h0, fb) where fb=(1,-1,0)
  This creates a triangular hole at the "top" between fl and fr.
  But then h0,h1,h2 are not collinear relative to the hole's inside angle.

  Better approach: 4-vertex collinear hole loop where the four hole verts are on
  X-axis and a single cross-bridge closes the loop.
    h0=(0,0,0), h1=(1,0,0), h2=(2,0,0), h3=(3,0,0)
    Top bridge: t0=(h0,h1,fa), t1=(h1,h2,fa), t2=(h2,h3,fa) where fa=(1.5,2,0).
    Close loop: t3=(h3,h0,fb) where fb=(1.5,-1,0).
    Hole boundary: h0→h1→h2→h3→h0 — a 4-vertex loop.
    Interior angles at h1 and h2: flat (180°) since collinear. Gang = DBL_MAX.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me742",
    title="TriangulateHole_L439_angle_computation_failure: 4-vertex collinear hole boundary; interior angles at h1,h2 are 180 deg; gang stays DBL_MAX; return 0 (Branch 3)",
    defect_class="hole_in_hull",
)

# Collinear hole-boundary vertices on the X-axis.
h0 = m.vertex(0.0, 0.0, 0.0)    # 0 — hole rim left
h1 = m.vertex(1.0, 0.0, 0.0)    # 1 — collinear inner vertex
h2 = m.vertex(2.0, 0.0, 0.0)    # 2 — collinear inner vertex
h3 = m.vertex(3.0, 0.0, 0.0)    # 3 — hole rim right

# Frame vertices bridging the hole.
fa = m.vertex(1.5, 2.0, 0.0)    # 4 — top frame apex
fb = m.vertex(1.5, -1.0, 0.0)   # 5 — bottom bridge apex

# Top fan: three triangles covering top half, sharing fa.
t0 = m.triangle(h0, h1, fa)    # 0 — top-left
t1 = m.triangle(h1, h2, fa)    # 1 — top-center; shares (h1,fa) with t0
t2 = m.triangle(h2, h3, fa)    # 2 — top-right; shares (h2,fa) with t1

# Bottom bridge: one triangle closing the loop at the bottom.
t3 = m.triangle(h3, h0, fb)    # 3 — bottom bridge

# Interior edges (n=2): top fan spoke sharing.
m.assert_edge_shared(h1, fa, 2)   # t0 and t1
m.assert_edge_shared(h2, fa, 2)   # t1 and t2

# Hole boundary edges (n=1): the collinear 4-vertex loop h0→h1→h2→h3→h0.
m.assert_edge_shared(h0, h1, 1)   # t0 bottom-left
m.assert_edge_shared(h1, h2, 1)   # t1 bottom
m.assert_edge_shared(h2, h3, 1)   # t2 bottom-right
m.assert_edge_shared(h3, h0, 1)   # t3 top (the bridge)

# Outer spoke edges (n=1).
m.assert_edge_shared(h0, fa, 1)   # t0 left spoke
m.assert_edge_shared(h3, fa, 1)   # t2 right spoke
m.assert_edge_shared(h0, fb, 1)   # t3 left spoke
m.assert_edge_shared(h3, fb, 1)   # t3 right spoke

# The collinear hole loop: h0→h1→h2→h3→h0.
# All vertices are on the X-axis; h1 and h2 have angle=180° (collinear).
m.assert_hole_boundary([h0, h1, h2, h3])

# Euler: V=6, E=10, F=4, chi=0 (annular topology — hole loop separate from outer boundary).
m.assert_euler_characteristic(6, 10, 4, 0)
