"""Me077 — duplicate_singular_vertices: CCW-only traversal (link reaches boundary, needs ccw walk).

Catalog claim: vertex 0 is a non-manifold (singular) vertex where the upper fan
is an open strip that can be traversed clockwise to reach one boundary edge but
then must switch to CCW traversal (Branch 9, *link_traversal_ccw*) to visit
the remaining triangle on the other side of the fan before seeing the second
boundary. In contrast the lower fan is completely separate.

This exercises Branch 7 (*link_traversal_cw*) crossing to an opposite-side fan
member AND Branch 9 (*link_traversal_ccw*) walking in the reverse direction.

Layout:
  Upper fan (open strip of 3 triangles with v0 in the interior):
    t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4)
    Edges at v0: (v0,v1) boundary, (v0,v2) shared t0/t1, (v0,v3) shared t1/t2,
                  (v0,v4) boundary.
    CW from t0: walk to t1 (via (v0,v2)), then to t2 (via (v0,v3)), then (v0,v4)
    is a boundary → switch to CCW from t0: walk back via (v0,v1) boundary → done.
  Lower fan (separate, single triangle):
    t3=(v0,v5,v6)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me077",
             title="duplicate_singular_vertices: open-strip fan (CW+CCW traversal) plus isolated lower fan",
             defect_class="non_manifold_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — singular bowtie vertex

# Upper open-strip fan outer rim.
v1 = m.vertex(-2.0, 1.0, 0.0)  # 1 — leftmost outer
v2 = m.vertex(-1.0, 1.0, 0.0)  # 2 — inner-left outer
v3 = m.vertex(0.0, 1.5, 0.0)   # 3 — top outer
v4 = m.vertex(1.0, 1.0, 0.0)   # 4 — rightmost outer

# Lower isolated fan.
v5 = m.vertex(1.0, -1.0, 0.0)  # 5
v6 = m.vertex(-1.0, -1.0, 0.0) # 6

# Upper fan — strip of 3 connected triangles.
t0 = m.triangle(v0, v1, v2)   # leftmost; (v0,v2) shared with t1
t1 = m.triangle(v0, v2, v3)   # middle; (v0,v2) shared with t0, (v0,v3) shared with t2
t2 = m.triangle(v0, v3, v4)   # rightmost; (v0,v3) shared with t1

# Lower isolated fan.
t3 = m.triangle(v0, v5, v6)

# Interior edges within the upper fan.
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)   # shared by t1 and t2

# Boundary edges of the upper fan.
m.assert_edge_shared(v0, v1, 1)   # left boundary of strip
m.assert_edge_shared(v0, v4, 1)   # right boundary of strip

# Boundary edges of the lower fan.
m.assert_edge_shared(v0, v5, 1)
m.assert_edge_shared(v0, v6, 1)

# v0's link has 2 CCs: upper strip (t0+t1+t2) vs. lower fan (t3).
m.assert_vertex_fan_disconnected(v0)
