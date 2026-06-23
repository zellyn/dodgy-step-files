"""Me261 — range_with_face_set_link_condition_violated: zero-length edge fails link condition.

Catalog claim: CGAL PMP.remove_degenerate_edges.range_with_face_set Branch 2 @ line 1581
(*zero_length_link_condition_violated*): the degenerate edge has zero length but
does_satisfy_link_condition returns false. The algorithm must then call
remove_a_border_edge or explore a more complex removal path (marked_faces strategy).

The link condition is violated when collapsing the near-coincident vertices would create a
non-manifold (bowtie) vertex: the link rings of v0 and v1 share more than just the edge
endpoints. In this fixture, the same vertex v3 appears in both the upper neighbourhood of
v0 and the lower neighbourhood of v1, so the link-condition intersection is non-empty —
collapsing would create a repeated vertex in the merged neighbourhood.

Geometric signature: a diamond where v0≈v1 (zero-length edge) and both v0 and v1 are
connected to the SAME opposite vertex v2 (above) and v3 (below). This means their
neighbourhoods overlap at v2 and v3, violating the link condition.

  t0 = (v0, v1, v2)   — shares degenerate edge; v0→v2, v1→v2
  t1 = (v1, v0, v3)   — shares degenerate edge; v0→v3, v1→v3
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me261",
             title="range_with_face_set link_condition_violated: zero-length edge v0≈v1 with shared neighbours → link condition fails",
             defect_class="degenerate_edge")

# Near-coincident vertex pair.
v0 = m.vertex(0.0,  0.0, 0.0)
v1 = m.vertex(1e-10, 0.0, 0.0)   # nearly same as v0

# Both vertices connect to the SAME two outer vertices — link condition violated.
v2 = m.vertex(0.0,  1.0, 0.0)    # above: appears in both link rings
v3 = m.vertex(0.0, -1.0, 0.0)    # below: appears in both link rings

# Two triangles sharing the degenerate edge, forming a flat diamond.
t0 = m.triangle(v0, v1, v2)   # 0: upper diamond face (degenerate edge + v2)
t1 = m.triangle(v1, v0, v3)   # 1: lower diamond face (degenerate edge + v3)

# The degenerate edge (v0,v1) is interior (shared by t0 and t1).
m.assert_edge_shared(v0, v1, 2)

# v0 and v1 are nearly coincident.
m.assert_vertex_pair_distance_lt(v0, v1, 1e-9)

# Both triangles share the same near-degenerate area (v0≈v1 so triangles are almost flat).
m.assert_triangle_area_lt(t0, 1e-7)
m.assert_triangle_area_lt(t1, 1e-7)
