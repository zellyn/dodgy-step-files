"""Me701 — Basic_TMesh.bridgeBoundaries branch 2: common_vertex_exists.

MeshFix `Basic_TMesh.bridgeBoundaries` Branch 2 (*common_vertex_exists*) @ line 432:
  'if ((cv = gve->commonVertex(gwe)) != NULL) { EulerEdgeTriangle(gve, gwe); return gve; }'
  — when two boundary edges share exactly one vertex, a single triangle
  bridges the gap: EulerEdgeTriangle fills the V-shaped notch with one
  new face and returns immediately.

Defect pattern: three triangles forming a fan around a central vertex, with
  an open V-notch between two boundary edges that share that center vertex.
  The two boundary edges (v0,v2) and (v1,v2) both meet at v2 — the common
  vertex. bridgeBoundaries detects this and emits one bridge triangle
  (v0,v1,v2), closing the notch.

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(0,2,0), v4=(2,2,0)
  t0=(v0,v1,v2) — bottom triangle
  t1=(v0,v2,v3) — left triangle (shares edge v0,v2 — interior)
  t2=(v1,v4,v2) — right triangle (shares edge v1,v2 — interior)
  Boundary edges on the open notch: (v0,v1) n=1.
  Shared-but-boundary edges: (v0,v2) is interior to t0,t1; (v1,v2) interior to t0,t2.
  Outer boundary: (v0,v3), (v3,v2), (v2,v4), (v4,v1), (v0,v1) each n=1.

  Simpler design: a strip of two triangles where two boundary edges meet at
  one shared vertex — makes it immediately clear that the common vertex exists.

  Two triangles t0=(v0,v1,v2), t1=(v1,v2,v3) sharing edge (v1,v2).
  Boundary edges: (v0,v1) n=1, (v0,v2) n=1, (v1,v3) n=1, (v2,v3) n=1.
  gve = (v0,v2), gwe = (v2,v3) share vertex v2 → Branch 2 fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me701",
    title="bridgeBoundaries common_vertex_exists: boundary edges (v0,v2) and (v2,v3) share vertex v2; single-triangle EulerEdgeTriangle bridge (Branch 2)",
    defect_class="boundary_hole",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — bottom-left
v1 = m.vertex(2.0, 0.0, 0.0)  # 1 — bottom-right
v2 = m.vertex(1.0, 1.0, 0.0)  # 2 — center (shared boundary vertex)
v3 = m.vertex(2.0, 2.0, 0.0)  # 3 — top-right

# Two triangles sharing interior edge (v1, v2).
t0 = m.triangle(v0, v1, v2)  # 0: bottom triangle
t1 = m.triangle(v1, v3, v2)  # 1: right triangle

# Interior shared edge (v1, v2) — n=2.
m.assert_edge_shared(v1, v2, 2)

# Boundary edges — each shared by exactly 1 triangle.
m.assert_edge_shared(v0, v1, 1)  # t0 bottom
m.assert_edge_shared(v0, v2, 1)  # t0 left — gve candidate
m.assert_edge_shared(v2, v3, 1)  # t1 top  — gwe candidate sharing v2 with gve
m.assert_edge_shared(v1, v3, 1)  # t1 right

# Hole boundary loop: the open gap is the notch at v2, between gve and gwe.
m.assert_hole_boundary([v0, v2, v3])

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
