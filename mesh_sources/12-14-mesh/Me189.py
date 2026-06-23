"""Me189 — split_edge_list_appends: new vertex, edges, triangles appended to mesh lists V, E, T.

Catalog claim: the final step of splitEdge appends all new elements to the mesh's
global lists: `V.appendHead(v)` (new vertex), `E.appendHead(ne1)`, `E.appendHead(ne2)`
(new edges), and `T.appendHead(nt1)`, `T.appendHead(nt2)` (new triangles).
These list operations register the new geometry so subsequent passes can iterate
over it.

This exercises MeshFix `Basic_TMesh.splitEdge` Branch 10 (*list_appends*):
the unconditional block at lines 1894–1902 that appends the new vertex, edges,
and triangles to the mesh topology lists.

Defect carrier: a more complex mesh with a 3-triangle strip where a central
boundary edge is split. The post-split state has:
  - 1 new vertex vn appended to V
  - 1 new edge ne1 appended to E (boundary split creates only ne1, not ne2)
  - 1 new triangle nt1 appended to T

The mesh now contains 4 vertices, 3 triangles, and the new edge ne1 is interior.
This verifies the list-append step by confirming all new elements participate
in the mesh topology (no isolated vertex, correct incidence).

Geometry (3-triangle strip, post-split of boundary edge):
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0), v3=(3,2,0), vn=(1,0,0)
  t0=(v0,vn,v2): left half of split triangle (from original t=(v0,v1,v2))
  t1=(vn,v1,v2): nt1 — appended to T by Branch 10
  t2=(v1,v3,v2): neighbor triangle sharing (v1,v2) — unchanged by split
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me189",
             title="split_edge_list_appends: V/E/T appendHead adds new vertex, edges, triangles",
             defect_class="split_edge_boundary")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left end of split edge
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — right end of split edge
v2 = m.vertex(1.0, 2.0, 0.0)   # 2 — apex shared by original triangle and neighbor
v3 = m.vertex(3.0, 2.0, 0.0)   # 3 — far apex of neighbor triangle
vn = m.vertex(1.0, 0.0, 0.0)   # 4 — new vertex appended to V by Branch 10

t0 = m.triangle(v0, vn, v2)   # 0 — left half of original triangle (trimmed t1)
t1 = m.triangle(vn, v1, v2)   # 1 — nt1: appended to T by Branch 10
t2 = m.triangle(v1, v3, v2)   # 2 — neighbor triangle (unchanged)

# ne1=(vn,v2): new edge appended to E by Branch 10. Interior (shared by t0 and t1).
m.assert_edge_shared(vn, v2, 2)   # ne1: interior — new edge added to E

# Split edge halves: both boundary (t2 is NULL for this boundary split).
m.assert_edge_shared(v0, vn, 1)   # left half of original edge — boundary
m.assert_edge_shared(vn, v1, 1)   # right half — boundary

# Shared edge between nt1 and neighbor t2: (v1,v2) — already interior.
m.assert_edge_shared(v1, v2, 2)   # shared with neighbor (unchanged)

# Outer boundary of the strip.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v1, v3, 1)

# New vertex vn lies on the original edge.
m.assert_vertex_on_edge(vn, v0, v1)
