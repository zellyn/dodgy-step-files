"""Me743 — TriangulateHole_L439_euler_edge_triangle_failure: EulerEdgeTriangle(e1,e2)==NULL; mark vertex bad and continue (Branch 4).

MeshFix `holeFilling::TriangulateHole` Branch 4 (*EULER_EDGE_TRIANGLE_FAILURE*) @ line 480:
  'if (EulerEdgeTriangle(e1,e2)==NULL) { MARK_BIT(v,5); continue; }'
  During hole triangulation, the algorithm selects a candidate vertex v with the
  smallest internal angle and attempts to create a new triangle by calling
  EulerEdgeTriangle(e1,e2). If this Euler operation returns NULL — because the
  proposed triangle would create a degenerate or duplicate topology (e.g. an edge
  that already connects the same two vertices) — the algorithm marks vertex v as
  "bad" (bit 5) and continues to the next candidate.

Defect pattern: a mesh where the hole-filling algorithm would attempt to create
  a triangle by linking two hole-rim edges, but the opposite vertex of the
  proposed triangle already shares an edge with both endpoints of the seed edge.
  This makes the new triangle topologically degenerate — EulerEdgeTriangle returns
  NULL and Branch 4 fires.

Geometry:
  Five-vertex "bowtie hole" configuration.
  v0=(0,0,0), v1=(2,0,0) — the seed edge (boundary).
  v2=(1,2,0) — the hole-rim vertex opposite the seed edge.
  v3=(1,0,0) — a vertex already connected to both v0 and v1 via existing interior
    edges; this creates the topology conflict for the Euler operation.
  v4=(1,-1,0) — bottom bridge vertex.

  Hole boundary: v0→v1→v2→v0 (triangular hole).
  But v3 is already connected to both v0 and v1 (interior edges), so when the
  algorithm tries to create triangle (v0,v1,v2) the Euler operation fails because
  v3 already spans v0-v1 making the new edge (v0,v1) degenerate in the context
  of the half-edge data structure.

  Specifically: edge (v0,v1) exists as a boundary edge (n=1) in frame triangle
  t0=(v0,v1,v4). The hole rim is v0→v1→v2→v0, so v2 is the candidate vertex.
  But v3 is interior-connected to v0 and v1 forming t1=(v0,v3,v2) and t2=(v1,v2,v3)
  — edges (v0,v2) and (v1,v2) are already interior (n=2). When the hole-fill
  tries EulerEdgeTriangle on those, it returns NULL.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me743",
    title="TriangulateHole_L439_euler_edge_triangle_failure: proposed triangle edges already interior (n=2); EulerEdgeTriangle returns NULL; MARK_BIT(v,5); continue (Branch 4)",
    defect_class="hole_in_hull",
)

# Core vertices.
v0 = m.vertex(0.0, 0.0, 0.0)    # 0 — hole left endpoint
v1 = m.vertex(2.0, 0.0, 0.0)    # 1 — hole right endpoint
v2 = m.vertex(1.0, 2.0, 0.0)    # 2 — hole apex vertex (candidate for filling)
v3 = m.vertex(1.0, 1.0, 0.0)    # 3 — interior vertex already connected to v0,v1,v2
v4 = m.vertex(1.0, -1.0, 0.0)   # 4 — bottom bridge apex

# Frame triangle below the hole — establishes (v0,v1) as the seed boundary edge.
t0 = m.triangle(v0, v1, v4)     # 0 — bottom frame; (v0,v1) becomes boundary (n=1)

# Interior triangles that create the conflict:
# t1 and t2 together fill the "hole" with interior edges, making the edges
# (v0,v2) and (v1,v2) interior (n=2 from the perspective of the hole filling).
t1 = m.triangle(v0, v3, v2)     # 1 — left interior fan
t2 = m.triangle(v1, v2, v3)     # 2 — right interior fan; shares (v2,v3) with t1

# Additional outer context triangles to make the hole visible as a hole.
v5 = m.vertex(-1.0, 1.0, 0.0)   # 5 — outer left
v6 = m.vertex(3.0, 1.0, 0.0)    # 6 — outer right
t3 = m.triangle(v0, v2, v5)     # 3 — outer left frame
t4 = m.triangle(v1, v6, v2)     # 4 — outer right frame

# Edge (v0,v1): seed edge — boundary from t0 only (n=1).
m.assert_edge_shared(v0, v1, 1)

# Edges (v0,v2) and (v1,v2): interior from t1+t3 and t2+t4 respectively (n=2).
# These are the edges EulerEdgeTriangle would try to create → already exist → NULL.
m.assert_edge_shared(v0, v2, 2)   # t1 and t3 share this
m.assert_edge_shared(v1, v2, 2)   # t2 and t4 share this

# Interior edge (v2,v3): shared by t1 and t2 (n=2).
m.assert_edge_shared(v2, v3, 2)

# Boundary edges from frame triangles.
m.assert_edge_shared(v0, v4, 1)   # t0 left base
m.assert_edge_shared(v1, v4, 1)   # t0 right base
m.assert_edge_shared(v0, v3, 1)   # t1 left side
m.assert_edge_shared(v1, v3, 1)   # t2 right side
m.assert_edge_shared(v0, v5, 1)   # t3 left outer
m.assert_edge_shared(v2, v5, 1)   # t3 top outer
m.assert_edge_shared(v1, v6, 1)   # t4 right outer
m.assert_edge_shared(v2, v6, 1)   # t4 top outer

# Euler: V=7, E=14, F=5*... wait, let me recount.
# V=7 (v0..v6), F=5 (t0..t4).
# Interior edges (n=2): (v0,v2), (v1,v2), (v2,v3) = 3 edges.
# Boundary edges (n=1): (v0,v1),(v0,v4),(v1,v4),(v0,v3),(v1,v3),(v0,v5),(v2,v5),(v1,v6),(v2,v6) = 9 edges.
# Total E = 3+9 = 12.
# chi = V-E+F = 7-12+5 = 0 (two boundary components: outer + inner).
m.assert_euler_characteristic(7, 12, 5, 0)
