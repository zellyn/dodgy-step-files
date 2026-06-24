"""Me463 — selectConnectedComponent neighbor_t2_enqueue: t2 reachable via e2 (non-sharp).

Catalog claim: Basic_TMesh.selectConnectedComponent Branch 4 @ line 1079
(*neighbor_t2_enqueue*): while processing triangle t, the BFS checks:
  `if (t2 != NULL && !IS_VISITED(t2) && (!sos || !IS_SHARPEDGE(t->e2)))`
and enqueues the neighbor t2 across edge e2 when that edge is NOT a sharp edge.

Edge e2 is a different edge of the same triangle from e1 (edge opposite vertex 2,
i.e., the edge between vertices 0 and 1 in 0-indexed MeshFix convention). Branch 4
fires after Branch 3 check, covering the second neighbor enqueue within the same
BFS dequeue step.

Note on sharp-edge state: IS_SHARPEDGE is a runtime flag on edge objects, not
directly representable in the fixture schema. This fixture documents the topological
precondition — a mesh with the center triangle t0 having a neighbor t2 across its
e2 edge where e2 is NOT marked sharp. Non-sharp is the default state; Branch 4
fires in a standard BFS call with sos=false.

Geometric signature: three triangles arranged so the seed triangle t0 has a distinct
neighbor across its e2 edge. To isolate Branch 4 (t2/e2) from Branch 3 (t1/e1),
one side of t0 is a boundary edge (no neighbor for e1) and e2 connects to t2.

  t0 = (v0, v1, v2)  — seed; e2 = edge(v0,v1) in MeshFix convention; t2-neighbor across e2
  t2 = (v1, v0, v3)  — t2-neighbor of t0, shares edge (v0,v1) = e2
  t3 = (v1, v2, v4)  — additional triangle so t0 also has a t1 path via (v1,v2)

Using 3 triangles to ensure e2 neighbor is unambiguously the second BFS enqueue step.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me463",
             title="selectConnectedComponent neighbor_t2_enqueue: BFS enqueues t2 across non-sharp edge e2",
             defect_class="disconnected_components")

# Five vertices; t0 is the seed with t2-neighbor across its bottom edge (v0,v1).
v0 = m.vertex(0.0,  0.0, 0.0)
v1 = m.vertex(2.0,  0.0, 0.0)
v2 = m.vertex(1.0,  2.0, 0.0)   # apex of seed triangle
v3 = m.vertex(1.0, -2.0, 0.0)   # below the seed; forms t2-neighbor
v4 = m.vertex(3.0,  1.0, 0.0)   # right; forms an additional neighbor

# Seed triangle and its two neighbors.
t0 = m.triangle(v0, v1, v2)    # 0: seed; e2 = edge(v0,v1) (bottom); t2-neighbor is t1 below
t1 = m.triangle(v1, v0, v3)    # 1: t2-neighbor of t0 across (v0,v1); enqueued via Branch 4
t2 = m.triangle(v1, v2, v4)    # 2: t1-neighbor of t0 across (v1,v2); enqueued via Branch 3

# The e2 edge (v0,v1) is interior — this is the non-sharp edge Branch 4 crosses.
m.assert_edge_shared(v0, v1, 2)

# The e1 edge (v1,v2) is also interior — shared by t0 and t2.
m.assert_edge_shared(v1, v2, 2)

# Remaining edges are boundary.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v4, 1)
m.assert_edge_shared(v1, v4, 1)

# All three triangles are one connected component.
# Euler: V=5, E=7 (2 interior + 5 boundary), F=3, chi = 5 - 7 + 3 = 1.
m.assert_euler_characteristic(v=5, e=7, f=3, chi=1)

# Note: Branch 4 fires during the BFS dequeue of t0 when t2 (here fixture triangle t1)
# is checked and found non-NULL, unvisited, and with non-sharp e2 edge.
