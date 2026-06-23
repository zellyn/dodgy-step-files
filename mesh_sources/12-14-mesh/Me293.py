"""Me293 — connected_components visited_face_dedup_inner: inner-queue dedup skips face already handled.

Catalog claim: CGAL PMP.connected_components Branch 4 @ line 234
(*Visited_vertex_dedup*): `if (!handled[fq_id])` — inside the BFS
while-loop, each face popped from the queue is checked again before
processing; faces already marked handled (reached via a different
neighboring face's halfedge) are skipped without re-labelling.

Geometric signature: a mesh where the same face is reachable from
multiple BFS predecessors simultaneously. A "diamond" of four triangles
sharing a common interior vertex demonstrates this: when BFS processes
face f0 it pushes f1 and f3 (neighbors via two of f0's edges). When BFS
then processes f1, it discovers f2 and f0-back (already handled). When it
processes f3, it discovers f2 again. Face f2 would be pushed twice by
different predecessors — Branch 4's `!handled[fq_id]` guard ensures
f2 is only labelled once.

Source: CGAL PMP.connected_components Branch 4 @ line 234
(*Visited_vertex_dedup*) — `while` body's `if (!handled[fq_id])` skip
guard prevents re-labelling faces discovered via multiple BFS paths.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me293",
             title="connected_components visited_face_dedup_inner: diamond mesh where center face is discoverable from two BFS paths",
             defect_class="disconnected_components")

# Diamond of 4 triangles: f0 (top), f1 (left), f2 (right), f3 (bottom).
# Layout: v0=top, v1=left, v2=right, v3=bottom, v4=center.
#
#        v0
#       /  \
#     f0    (not adjacent to center directly)
#    /  \
#  v1 -- v4 -- v2
#    \  /  \  /
#     f1    f2
#       \  /
#        v3
#
# Simpler diamond:
# f0 = (v0,v1,v4): top-left
# f1 = (v0,v4,v2): top-right  (both f0 and f1 share edge (v0,v4))
# f2 = (v1,v3,v4): bottom-left
# f3 = (v4,v3,v2): bottom-right
# BFS from f0: pushes f1 (via v0,v4) and f2 (via v1,v4).
# Processing f1: pushes f3 (via v4,v2), checks (v0,v4) → f0 already handled.
# Processing f2: pushes f3 (via v3,v4) again → Branch 4 fires.

v0 = m.vertex(1.0, 2.0, 0.0)    # 0 — top
v1 = m.vertex(0.0, 0.0, 0.0)    # 1 — left
v2 = m.vertex(2.0, 0.0, 0.0)    # 2 — right
v3 = m.vertex(1.0, -2.0, 0.0)   # 3 — bottom
v4 = m.vertex(1.0, 0.0, 0.0)    # 4 — center

f0 = m.triangle(v0, v1, v4)   # face 0: top-left; BFS seed
f1 = m.triangle(v0, v4, v2)   # face 1: top-right; shares (v0,v4) with f0
f2 = m.triangle(v1, v3, v4)   # face 2: bottom-left; shares (v1,v4) with f0
f3 = m.triangle(v4, v3, v2)   # face 3: bottom-right; shares (v3,v4) with f2, (v2,v4) with f1

# Shared interior edges.
m.assert_edge_shared(v0, v4, 2)   # f0 and f1
m.assert_edge_shared(v1, v4, 2)   # f0 and f2
m.assert_edge_shared(v3, v4, 2)   # f2 and f3
m.assert_edge_shared(v2, v4, 2)   # f1 and f3

# All 4 faces form one CC — f3 reachable from f0.
# (Confirmed by absence of not_reachable assertion between them.)

# Disconnected component for defect_class.
w0 = m.vertex(10.0, 0.0, 0.0)   # 5
w1 = m.vertex(11.0, 0.0, 0.0)   # 6
w2 = m.vertex(10.5, 1.0, 0.0)   # 7
iso = m.triangle(w0, w1, w2)   # face 4: isolated second CC

m.assert_triangle_not_reachable_from(iso, f0)
