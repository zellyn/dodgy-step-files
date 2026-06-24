"""Me464 — selectConnectedComponent neighbor_t3_enqueue: t3 reachable via e3 (non-sharp).

Catalog claim: Basic_TMesh.selectConnectedComponent Branch 5 @ line 1080
(*neighbor_t3_enqueue*): while processing triangle t, the BFS checks:
  `if (t3 != NULL && !IS_VISITED(t3) && (!sos || !IS_SHARPEDGE(t->e3)))`
and enqueues the neighbor t3 across edge e3 when that edge is NOT a sharp edge.

Edge e3 is the third edge of the triangle (opposite vertex 3, i.e., the edge between
vertices 1 and 2 in 0-indexed MeshFix convention). Branch 5 fires after Branches 3
and 4, covering the third and final neighbor enqueue for a given triangle.

The key contrast case for Branch 5 is when the sharp-edge `sos` flag IS true and e3
IS marked as a sharp edge — in that case the condition is false and t3 is NOT enqueued,
creating a "sharp-edge barrier" that limits the connected component. This fixture
shows the topological precondition for the NON-blocking traversal (sos=false or e3
not sharp), where t3 is enqueued.

Note on sharp-edge state: IS_SHARPEDGE is a runtime flag, not representable in the
fixture schema. This fixture documents the topology where the e3-neighbor (t3) exists
and is unvisited. Sharp-edge blocking is the negative complement of this branch.

Geometric signature: five triangles where the seed t0 has neighbors across all three
edges. The e3-neighbor (across the third edge, between v1 and v2) is a fresh triangle
t3_nbr that has not yet been visited when Branch 5 fires.

  t0 = (v0, v1, v2)  — seed; e3 edge = (v1,v2); t3-neighbor = t3_nbr
  t1_nbr = (v2, v0, v3)  — e1-neighbor (across v0,v2)
  t2_nbr = (v1, v0, v4)  — e2-neighbor (across v0,v1)
  t3_nbr = (v2, v1, v5)  — e3-neighbor (across v1,v2) — this is the Branch 5 target
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me464",
             title="selectConnectedComponent neighbor_t3_enqueue: BFS enqueues t3 across non-sharp edge e3",
             defect_class="disconnected_components")

# Six vertices — seed triangle and three neighbors, one per edge.
v0 = m.vertex(0.0,  0.0, 0.0)   # vertex 0 of seed
v1 = m.vertex(2.0,  0.0, 0.0)   # vertex 1 of seed
v2 = m.vertex(1.0,  2.0, 0.0)   # vertex 2 of seed (apex)
v3 = m.vertex(-1.0, 1.0, 0.0)   # e1-neighbor outer vertex (across v0,v2)
v4 = m.vertex(1.0, -2.0, 0.0)   # e2-neighbor outer vertex (across v0,v1)
v5 = m.vertex(3.5,  1.5, 0.0)   # e3-neighbor outer vertex (across v1,v2) — Branch 5 target

# Seed triangle.
t0 = m.triangle(v0, v1, v2)      # 0: seed; all 3 edges are interior

# Three neighbor triangles, one per edge.
t1_nbr = m.triangle(v2, v0, v3)  # 1: e1-neighbor of t0 (shares v0,v2)
t2_nbr = m.triangle(v1, v0, v4)  # 2: e2-neighbor of t0 (shares v0,v1)
t3_nbr = m.triangle(v2, v1, v5)  # 3: e3-neighbor of t0 (shares v1,v2) — Branch 5 enqueues this

# All three edges of t0 are interior (shared with one neighbor each).
m.assert_edge_shared(v0, v2, 2)   # e1 of t0
m.assert_edge_shared(v0, v1, 2)   # e2 of t0
m.assert_edge_shared(v1, v2, 2)   # e3 of t0 — Branch 5 crosses this

# Outer boundary edges of each neighbor.
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v1, v4, 1)
m.assert_edge_shared(v1, v5, 1)
m.assert_edge_shared(v2, v5, 1)

# All 4 triangles form one connected component.
# Euler: V=6, E=9 (3 interior + 6 boundary), F=4, chi = 6 - 9 + 4 = 1.
m.assert_euler_characteristic(v=6, e=9, f=4, chi=1)

# Note: Branch 5 fires when t0 is dequeued and t3_nbr (across e3 = (v1,v2)) is found
# non-NULL, unvisited, and e3 is not marked sharp. With sos=true and SHARPEDGE(e3)=true,
# the BFS would stop at v1-v2, leaving t3_nbr in a separate component.
