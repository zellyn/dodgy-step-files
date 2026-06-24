"""Me515 — Edge.swap branch 6: INCIDENT_EDGE_UPDATE_E1.

MeshFix `Edge.swap` Branch 6 (*INCIDENT_EDGE_UPDATE_E1*) @ line 160:
  'e1->replaceTriangle(t1, t2); e3->replaceTriangle(t2, t1);'
  — the final step of the swap updates the incident-triangle links on the two
  outer edges e1 and e3. Before the swap, e1 was incident on t1; after the
  swap, t1 has been replaced by t2 in e1's triangle list, and e3's t2 becomes
  t1. This adjacency update is required to keep the mesh's half-edge structure
  consistent after the diagonal flip. Branch 6 fires for every successful swap.

Defect pattern: a 2-triangle quad where both outer edges e1 and e3 are each
  shared by exactly one triangle (boundary edges, n=1). After swap, e1 will be
  incident on the NEW t2 instead of the old t1, and e3 will be incident on the
  new t1 instead of t2. We assert that after the pre-swap configuration each
  outer edge correctly has n=1 (each still incident on one triangle), and that
  the post-swap diagonal (v1,v3) does not yet exist — the adjacency update is
  the last step that closes the swap.

Geometry (z=0):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(-0.5,0.5,0)
  t0=(v0,v1,v2) — triangle 0; e1=edge(v1,v2) is nextEdge of t0 after diagonal
  t1=(v0,v2,v3) — triangle 1; e3=edge(v2,v3) is nextEdge of t1 after diagonal

After swap: e1=(v1,v2) will belong to the new t2; e3=(v2,v3) will belong to
  the new t1. The replaceTriangle calls on e1 and e3 complete the adjacency
  update. Each of e1 and e3 has n=1 both before and after (they remain boundary).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me515",
    title="Edge.swap INCIDENT_EDGE_UPDATE_E1: outer edges e1=(v1,v2) and e3=(v2,v3) each incident on one triangle; e1->replaceTriangle(t1,t2) and e3->replaceTriangle(t2,t1) complete adjacency update (Branch 6)",
    defect_class="edge_swap_incident_edge_update",
)

v0 = m.vertex(0.0,  0.0,  0.0)   # 0 — shared diagonal bottom endpoint
v1 = m.vertex(1.0,  0.0,  0.0)   # 1 — opposite vertex of t0; e1 links to t0
v2 = m.vertex(0.5,  1.0,  0.0)   # 2 — shared diagonal top endpoint
v3 = m.vertex(-0.5, 0.5,  0.0)   # 3 — opposite vertex of t1; e3 links to t1

# Two-triangle quad with shared diagonal (v0,v2).
t0 = m.triangle(v0, v1, v2)   # 0: left triangle — owns outer edge e1=(v1,v2)
t1 = m.triangle(v0, v2, v3)   # 1: right triangle — owns outer edge e3=(v2,v3)

# Interior diagonal (v0,v2) — shared by both triangles.
m.assert_edge_shared(v0, v2, 2)

# Outer edges e1=(v1,v2) and e3=(v2,v3) each incident on one triangle.
# These are the edges whose replaceTriangle calls fire in Branch 6.
m.assert_edge_shared(v1, v2, 1)   # e1 — owned by t0; will replaceTriangle(t1→t2)
m.assert_edge_shared(v2, v3, 1)   # e3 — owned by t1; will replaceTriangle(t2→t1)

# Other boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v3, 1)

# Post-swap diagonal (v1,v3) does not yet exist before swap completes.
m.assert_edge_shared(v1, v3, 0)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
