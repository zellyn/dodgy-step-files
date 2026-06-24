"""Me555 — checkAndRepair::rebuildConnectivity FIXCONNECTIVITY_REQUESTED: fixconnectivity flag triggers fixConnectivity() call (Branch 6).

MeshFix `checkAndRepair::rebuildConnectivity` Branch 6 (*FIXCONNECTIVITY_REQUESTED*) @ line 383:
  'if (fixconnectivity) fixConnectivity();'
  — after the main duplicate-vertex unification and triangle rebuild loop,
  if the fixconnectivity boolean flag was set when checkAndRepair was invoked,
  a second-pass fixConnectivity() call is made to resolve remaining topology
  defects such as orphan edges, T-junctions, or boundary stitching needs.
  This branch fires when fixconnectivity==true at the end of rebuildConnectivity.

Defect pattern: two separate triangles that share a common boundary vertex
  but whose edge connectivity is currently orphaned (neither triangle is reachable
  from the other via shared-edge traversal). The fixConnectivity() call stitches
  them into a manifold surface by linking the orphan half-edges. The fixture
  captures this by having a shared boundary vertex (s2) that is a fan-disconnected
  vertex between two triangles reachable only through that vertex, not through
  shared edges.

Geometry:
  s0=(0,0,0), s1=(2,0,0), s2=(1,2,0), s3=(3,2,0), s4=(1,4,0)
  t0=(s0,s1,s2): left triangle
  t1=(s2,s3,s4): right triangle — shares only vertex s2 with t0 (bowtie/orphan)
  t0 and t1 share the vertex s2 but no edge → fixConnectivity needed.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me555",
    title="checkAndRepair::rebuildConnectivity FIXCONNECTIVITY_REQUESTED: two triangles sharing vertex s2 but no edge (orphan fan); fixconnectivity flag set; fixConnectivity() called (Branch 6)",
    defect_class="connectivity_defect",
)

s0 = m.vertex(0.0, 0.0, 0.0)  # 0 — bottom-left
s1 = m.vertex(2.0, 0.0, 0.0)  # 1 — bottom-right
s2 = m.vertex(1.0, 2.0, 0.0)  # 2 — shared tip vertex (bowtie point)
s3 = m.vertex(3.0, 2.0, 0.0)  # 3 — upper-right
s4 = m.vertex(1.0, 4.0, 0.0)  # 4 — top apex

# Two triangles sharing only vertex s2 — no shared edge (bowtie / orphan).
t0 = m.triangle(s0, s1, s2)  # 0: lower triangle
t1 = m.triangle(s2, s3, s4)  # 1: upper triangle — only vertex s2 in common

# All edges are boundary edges (n=1) — no shared edge between t0 and t1.
m.assert_edge_shared(s0, s1, 1)  # t0 base
m.assert_edge_shared(s0, s2, 1)  # t0 left
m.assert_edge_shared(s1, s2, 1)  # t0 right
m.assert_edge_shared(s2, s3, 1)  # t1 left
m.assert_edge_shared(s2, s4, 1)  # t1 right
m.assert_edge_shared(s3, s4, 1)  # t1 top

# s2 is a fan-disconnected (bowtie) vertex — triangle fan has two components.
m.assert_vertex_fan_disconnected(s2)

# t1 is not reachable from t0 by walking shared edges (disconnected components).
m.assert_triangle_not_reachable_from(t1, t0)
