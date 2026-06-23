"""Me094 — edge_collapse_pinch_detect: v2 neighbor already connected to v1.

Catalog claim: vertex v0 is connected to v1 via the collapse edge. However, v0
also has a neighbor vertex tv that is ALREADY connected to v1 via another edge.
Collapsing v0 onto v1 would create a second edge between v1 and tv — a duplicate
edge, or "pinch". The MeshFix collapseOnV1 routine detects this and returns NULL.

This exercises MeshFix `Edge.collapseOnV1` Branch 8
(*PINCH_DETECT_ON_V2*): 'if (tv->getEdge(v1) != NULL && tv != v3 && tv != v4)'
— the loop over v0's incident vertices checks whether any neighbor (other than
the collapse triangle's apices v3 and v4) already has an edge to v1.

Defect carrier: a mesh where v0 and v1 are collapse candidates, and a third
vertex v5 is connected to both. This "shortcut" edge (v1, v5) already exists
independently of the collapse, so merging v0 into v1 would create a double edge
between v1 and v5.

Geometry (from above, XY plane):
  v0=(0,0,0), v1=(2,0,0)  — collapse edge
  v2=(1, 2,0)             — upper apex (t1)
  v3=(1,-2,0)             — lower apex (t2)
  v5=(2, 1,0)             — neighbor of BOTH v0 and v1 (the "pinch" vertex)

  t1: (v0, v1, v2)  — shares (v0,v1) with t2
  t2: (v0, v3, v1)
  t3: (v0, v5, v2)  — v0↔v5 edge
  t4: (v1, v2, v5)  — v1↔v5 edge already exists!

So v5 is a neighbor of v0 (via t3) AND already connected to v1 (via t4).
Collapsing v0→v1 would create two edges between v1 and v5.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me094",
             title="edge_collapse_pinch_detect: v0 neighbor already connected to v1, collapse blocked",
             defect_class="edge_collapse_pinch")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — vertex to collapse (v0/v2 in MeshFix)
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — collapse target (v1 in MeshFix)
v2 = m.vertex(1.0, 2.0, 0.0)   # 2 — upper apex for the main collapse triangle t1
v3 = m.vertex(1.0, -2.0, 0.0)  # 3 — lower apex for t2
v5 = m.vertex(2.0, 1.0, 0.0)   # 4 — the "pinch" vertex (neighbor of both v0 and v1)

# Main collapse edge (v0, v1) interior: shared by t_top and t_bot.
t_top = m.triangle(v0, v1, v2)   # 0 — t1
t_bot = m.triangle(v0, v3, v1)   # 1 — t2

# Triangle connecting v0 to v5.
t_left = m.triangle(v0, v5, v2)  # 2 — gives v0 a neighbor v5

# Triangle connecting v1 to v5 (the EXISTING edge that causes the pinch).
t_right = m.triangle(v1, v2, v5) # 3 — gives v1 an existing edge to v5

# The collapse edge (v0,v1) is interior.
m.assert_edge_shared(v0, v1, 2)   # collapse edge

# v5 is connected to BOTH v0 and v1 (each edge appears in one triangle only).
m.assert_edge_shared(v0, v5, 1)   # t_left only: v0↔v5 boundary edge
m.assert_edge_shared(v1, v5, 1)   # t_right only: v1↔v5 boundary edge (the "pinch" edge)

# v2 is shared apex — used by multiple triangles.
m.assert_edge_shared(v0, v2, 2)   # (t_top and t_left share this edge)
m.assert_edge_shared(v1, v2, 2)   # (t_top and t_right share this edge)
