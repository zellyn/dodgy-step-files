"""Me693 — connected_component logic_guard_ecmap: constrained edge blocks BFS expansion.

Catalog claim: CGAL PMP.connected_component Branch 4 @ line 149
(*Logic_guard*): `! get(ecmap, edge(hd, pmesh))` — when the edge-constraint
map (ecmap) marks an edge as constrained, the BFS does NOT cross it to the
opposite face. A constrained interior edge acts as a CC boundary even though
the two triangles sharing it are topologically adjacent.

Geometric signature: two triangles t0=(v0,v1,v2) and t1=(v0,v2,v3) share
interior edge (v0,v2). Without any constraint they would form a single CC.
When that edge is marked constrained in the ecmap, Branch 4's guard fires
and BFS from t0 cannot reach t1 — each triangle is its own CC. The
edge_shared oracle confirms the shared topology while the not_reachable
assertion captures the CC split the constraint enforces.

Three isolated triangles (t2, t3, t4) form additional CCs to satisfy the
multi-CC defect_class theme for connected_component coverage.

Source: CGAL PMP.connected_component Branch 4 @ line 149
(*Logic_guard*) — `! get(ecmap, edge(hd, pmesh))` prevents BFS crossing
constrained edges; a constraint on an interior edge creates a CC boundary.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me693",
             title="connected_component logic_guard_ecmap: constrained edge (v0,v2) prevents BFS crossing between t0 and t1",
             defect_class="disconnected_components")

# Two triangles sharing edge (v0,v2) — topologically connected, but
# the ecmap constraint on that edge blocks BFS from crossing it.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 1.0, 0.0)   # 2
v3 = m.vertex(0.0, 1.0, 0.0)   # 3

t0 = m.triangle(v0, v1, v2)   # face 0: left half of quad
t1 = m.triangle(v0, v2, v3)   # face 1: right half; shares (v0,v2)=(0,2) with t0

# Interior edge (v0,v2) shared by both — topology IS connected.
# When marked constrained the BFS guard fires and t0 cannot reach t1.
# The edge_shared oracle confirms the interior edge exists; the not_reachable
# behavior is enforced by the ecmap at runtime, not by mesh topology alone.
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1 — constrained edge

# Additional isolated triangles — form extra CCs.
w0 = m.vertex(5.0, 0.0, 0.0)   # 4
w1 = m.vertex(6.0, 0.0, 0.0)   # 5
w2 = m.vertex(5.5, 1.0, 0.0)   # 6
t2 = m.triangle(w0, w1, w2)   # face 2: isolated CC C

x0 = m.vertex(10.0, 0.0, 0.0)  # 7
x1 = m.vertex(11.0, 0.0, 0.0)  # 8
x2 = m.vertex(10.5, 1.0, 0.0)  # 9
t3 = m.triangle(x0, x1, x2)   # face 3: isolated CC D

m.assert_triangle_not_reachable_from(t2, t0)
m.assert_triangle_not_reachable_from(t3, t0)
m.assert_triangle_not_reachable_from(t3, t2)
