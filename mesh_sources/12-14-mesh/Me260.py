"""Me260 — range_with_face_set_link_condition_ok: zero-length edge satisfies link condition.

Catalog claim: CGAL PMP.remove_degenerate_edges.range_with_face_set Branch 1 @ line 1558
(*zero_length_link_condition_ok*): a degenerate edge has both endpoints at the same
position AND satisfies does_satisfy_link_condition, so the edge is directly collapsed
via Euler::collapse_edge.

The link condition is satisfied when collapsing the edge does not create a non-manifold
vertex: the open neighbourhood of the edge's endpoints, restricted to the triangles not
incident on the edge, must form a single connected region.

Geometric signature: three triangles forming a fan with a near-degenerate interior edge.
Vertices v0 and v1 are nearly coincident (distance ≈ 1e-10). The edge (v0,v1) is shared
by exactly 2 triangles (interior), and the opposite vertices v2 and v3 are distinct and
connected via t2, so the link condition is satisfied: collapsing v0→v1 yields no
non-manifold result.

  t0 = (v0, v1, v2) — first triangle sharing the degenerate edge
  t1 = (v1, v0, v3) — second triangle sharing the degenerate edge (same edge, opposite half)
  t2 = (v0, v2, v3) — closes the manifold neighbourhood
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me260",
             title="range_with_face_set link_condition_ok: zero-length edge v0≈v1 satisfies link condition for direct collapse",
             defect_class="degenerate_edge")

# Near-coincident vertex pair: v0 and v1 separated by distance ≈ 1e-10.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1e-10, 0.0, 0.0)   # nearly same as v0

# Two outer vertices completing the two triangles around the degenerate edge.
v2 = m.vertex(1.0,  1.0, 0.0)
v3 = m.vertex(-1.0, 1.0, 0.0)

# Both triangles share the degenerate edge (v0, v1).
t0 = m.triangle(v0, v1, v2)   # 0: uses degenerate edge
t1 = m.triangle(v1, v0, v3)   # 1: uses same degenerate edge (reversed half-edge)

# Third triangle closes the neighbourhood — link condition satisfied.
t2 = m.triangle(v0, v2, v3)   # 2: v2 and v3 connected, neighbourhood is a single disk

# The degenerate edge (v0, v1) has near-zero length.
m.assert_vertex_pair_distance_lt(v0, v1, 1e-9)

# The degenerate edge is interior: shared by exactly 2 triangles (t0 and t1).
m.assert_edge_shared(v0, v1, 2)

# All 3 triangles form one connected component — t2 is reachable from t0 via shared edges.
