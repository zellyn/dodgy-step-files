"""Me690 — connected_component loop_control: BFS while-loop iterates over a multi-face component.

Catalog claim: CGAL PMP.connected_component Branch 1 @ line 140
(*Loop_control*): the `while (!face_queue.empty())` loop drives the BFS
for a single connected component. A zigzag strip of five triangles sharing
edges forces the while-loop to cycle five times before the queue drains —
exercising the branch that keeps iteration going.

Geometric signature: five triangles arranged as a zigzag strip (t0-t4),
each adjacent pair sharing one interior edge. BFS seeded at t0 must run
five iterations through the while-loop before the queue empties. An
isolated triangle (t5) is topologically disconnected from the strip,
forming a second connected component.

Strip layout (4 base + 3 apex vertices):
  p0      p1      p2
  /\\t1  t2/\\t3  t4/\\
 /t0\\   /  \\   /  \\
b0   b1      b2    b3

t0=(b0,b1,p0); t1=(b1,p1,p0) shares (b1,p0) with t0;
t2=(b1,b2,p1) shares (b1,p1) with t1; t3=(b2,p2,p1) shares (b2,p1) with t2;
t4=(b2,b3,p2) shares (b2,p2) with t3.

Source: CGAL PMP.connected_component Branch 1 @ line 140
(*Loop_control*) — `while (!face_queue.empty())` drives the BFS;
the 5-triangle strip forces 5 iterations before the queue empties.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me690",
             title="connected_component loop_control: 5-triangle zigzag strip forces BFS while-loop to cycle 5 times",
             defect_class="disconnected_components")

# Zigzag strip vertices.
b0 = m.vertex(0.0, 0.0, 0.0)   # 0 — base left
b1 = m.vertex(1.0, 0.0, 0.0)   # 1 — base mid-left
b2 = m.vertex(2.0, 0.0, 0.0)   # 2 — base mid-right
b3 = m.vertex(3.0, 0.0, 0.0)   # 3 — base right

p0 = m.vertex(0.5, 1.0, 0.0)   # 4 — apex above (b0,b1)
p1 = m.vertex(1.5, 1.0, 0.0)   # 5 — apex above (b1,b2)
p2 = m.vertex(2.5, 1.0, 0.0)   # 6 — apex above (b2,b3)

# Strip of 5 triangles: each adjacent pair shares one edge.
t0 = m.triangle(b0, b1, p0)   # face 0: seed; boundary edges (b0,p0) and (b0,b1)
t1 = m.triangle(b1, p1, p0)   # face 1: shares edge (b1,p0)=(1,4) with t0
t2 = m.triangle(b1, b2, p1)   # face 2: shares edge (b1,p1)=(1,5) with t1
t3 = m.triangle(b2, p2, p1)   # face 3: shares edge (b2,p1)=(2,5) with t2
t4 = m.triangle(b2, b3, p2)   # face 4: shares edge (b2,p2)=(2,6) with t3

# Interior shared edges — each shared by exactly 2 triangles.
m.assert_edge_shared(b1, p0, 2)   # t0 and t1
m.assert_edge_shared(b1, p1, 2)   # t1 and t2
m.assert_edge_shared(b2, p1, 2)   # t2 and t3
m.assert_edge_shared(b2, p2, 2)   # t3 and t4

# Isolated triangle — second CC; outer BFS seeds new traversal here.
q0 = m.vertex(20.0, 0.0, 0.0)   # 7
q1 = m.vertex(21.0, 0.0, 0.0)   # 8
q2 = m.vertex(20.5, 1.0, 0.0)   # 9
iso = m.triangle(q0, q1, q2)   # face 5: isolated; unreachable from t0

m.assert_triangle_not_reachable_from(iso, t0)
