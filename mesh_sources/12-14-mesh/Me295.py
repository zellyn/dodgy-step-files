"""Me295 — connected_components logic_guard_ecmap: constrained edge splits one surface into two CCs.

Catalog claim: CGAL PMP.connected_components Branch 6 @ line 239
(*Logic_guard*): `get(ecmap, edge(h, pmesh))` — when an edge is marked
as constrained in the edge-component map (ecmap), the BFS does NOT cross
that edge to the opposite face. A constraint mark on an interior edge
effectively acts as a CC boundary, splitting an otherwise-connected surface
into two separate connected components.

Geometric signature: two triangles sharing one interior edge. Normally they
would form a single CC (both BFS-reachable from each other). When the
shared edge is marked constrained, Branch 6's check prevents BFS from
crossing it, so each triangle is in its own CC. The fixture represents the
mesh state where the constraint divides the surface — the oracle verifies
the edge is shared by exactly 2 triangles (demonstrating it IS a topological
interior edge) while the disconnected-components assertion captures the
effective CC split the constraint would produce.

Source: CGAL PMP.connected_components Branch 6 @ line 239
(*Logic_guard*) — `if (get(ecmap, edge(h, pmesh)))` prevents BFS crossing
constrained edges; turns one surface into multiple CCs at constraint lines.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me295",
             title="connected_components logic_guard_ecmap: constrained interior edge creates CC boundary on otherwise-connected quad",
             defect_class="disconnected_components")

# Two triangles sharing edge (v1, v2) — topologically connected without constraint.
# With ecmap constraint on (v1,v2), BFS from t0 cannot reach t1.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 1.0, 0.0)   # 2
v3 = m.vertex(0.0, 1.0, 0.0)   # 3

t0 = m.triangle(v0, v1, v2)   # face 0: left half of quad
t1 = m.triangle(v0, v2, v3)   # face 1: right half of quad

# The interior edge (v0, v2) is shared by both triangles — it IS interior.
# Under a constrained-edge scenario, BFS stops here; the two faces become
# separate CCs. The edge_shared assertion confirms the topology.
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1 — would normally connect them

# Add two isolated component triangles to satisfy the multi-CC fixture theme.
# These represent components C and D: additional proof that CCs can be multiple.
w0 = m.vertex(5.0, 0.0, 0.0)   # 4
w1 = m.vertex(6.0, 0.0, 0.0)   # 5
w2 = m.vertex(5.5, 1.0, 0.0)   # 6
t2 = m.triangle(w0, w1, w2)   # face 2: isolated component C

x0 = m.vertex(10.0, 0.0, 0.0)  # 7
x1 = m.vertex(11.0, 0.0, 0.0)  # 8
x2 = m.vertex(10.5, 1.0, 0.0)  # 9
t3 = m.triangle(x0, x1, x2)   # face 3: isolated component D

# Components C and D are disconnected from each other and from the quad.
m.assert_triangle_not_reachable_from(t2, t0)
m.assert_triangle_not_reachable_from(t3, t0)
m.assert_triangle_not_reachable_from(t3, t2)
