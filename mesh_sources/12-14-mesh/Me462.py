"""Me462 — selectConnectedComponent neighbor_t1_enqueue: t1 reachable via e1 (non-sharp).

Catalog claim: Basic_TMesh.selectConnectedComponent Branch 3 @ line 1078
(*neighbor_t1_enqueue*): while processing triangle t, the BFS checks:
  `if (t1 != NULL && !IS_VISITED(t1) && (!sos || !IS_SHARPEDGE(t->e1)))`
and enqueues the neighbor t1 across edge e1 when that edge is NOT a sharp edge.

In MeshFix's triangle data structure each triangle stores its three edge references
(e1, e2, e3) and corresponding opposite-triangle pointers (t1, t2, t3). Edge e1 is
the edge opposite vertex 1 (between vertices 0 and 2 in 0-indexed convention).
Branch 3 fires when t1 is not NULL, t1 is unvisited, and either the `sos` (stop-on-
sharp) flag is false OR edge e1 is not marked as sharp.

Note on sharp-edge state: IS_SHARPEDGE is a runtime flag on the edge object, not
representable in the fixture schema. This fixture documents the TOPOLOGICAL
precondition — a pair of triangles sharing edge e1 where that edge is NOT sharp.
The non-sharp condition is the normal case; a mesh with this topology will exercise
Branch 3 when the sos flag is false (default BFS call).

Geometric signature: two triangles sharing a single interior edge. The seed triangle
t0 has neighbor t1 across its shared edge. The BFS from t0 reaches t1 by firing
Branch 3 (t1 != NULL, not visited, edge not sharp).

  t0 = (v0, v1, v2)  — seed triangle; e1 = edge(v0,v2); t1 = neighbor across e1
  t1 = (v2, v0, v3)  — neighbor across edge (v0,v2); enqueued via Branch 3
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me462",
             title="selectConnectedComponent neighbor_t1_enqueue: BFS enqueues t1 across non-sharp edge e1",
             defect_class="disconnected_components")

# Four vertices forming two adjacent triangles sharing edge (v0,v2).
v0 = m.vertex(0.0,  0.0, 0.0)
v1 = m.vertex(2.0,  0.0, 0.0)
v2 = m.vertex(1.0,  2.0, 0.0)
v3 = m.vertex(-1.0, 1.0, 0.0)

# Seed triangle and its e1-neighbor.
t0 = m.triangle(v0, v1, v2)    # 0: seed; e1 is the edge between v0 and v2
t1 = m.triangle(v2, v0, v3)    # 1: t1-neighbor of t0; shares edge (v0,v2) = e1

# The shared edge (v0,v2) is interior — this is the non-sharp e1 edge that Branch 3 crosses.
m.assert_edge_shared(v0, v2, 2)

# Boundary edges (each incident on exactly 1 triangle).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# Both triangles form one connected component; the BFS must cross the shared edge once.
# Euler: V=4, E=5 (1 interior + 4 boundary), F=2, chi = 4 - 5 + 2 = 1 (open disk).
m.assert_euler_characteristic(v=4, e=5, f=2, chi=1)

# Note: the non-sharp status of edge (v0,v2) is the runtime precondition for Branch 3.
# In a selectConnectedComponent call with sos=false (default), all interior edges are
# traversed regardless of SHARPEDGE flag, so Branch 3 fires for this mesh.
