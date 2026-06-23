"""Me292 — connected_components loop_control: BFS while-loop runs until component exhausted.

Catalog claim: CGAL PMP.connected_components Branch 3 @ line 229
(*Loop_control*): the inner `while (!face_queue.empty())` loop drives the
BFS until every face in the current connected component is processed.
A fan of six triangles around one apex forces the while-loop to cycle
through all 6 faces before the queue empties.

Geometric signature: six triangles arranged as a fan sharing a common apex
vertex (component A, faces 0-5). Each adjacent pair shares one edge. The
BFS starting from face 0 discovers faces 1-5 through shared edges and must
run its while-loop until the queue drains after 6 iterations. An isolated
triangle (component B, face 6) requires a second BFS seed from the outer
loop, confirming the loop_control branch ran to completion for component A.

Source: CGAL PMP.connected_components Branch 3 @ line 229
(*Loop_control*) — `while (!face_queue.empty())` drives the BFS;
the six-triangle fan exhausts the queue only after visiting all 6 faces.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me292",
             title="connected_components loop_control: 6-triangle fan forces BFS while-loop to cycle until exhausted",
             defect_class="disconnected_components")

# Component A: 6-triangle fan around a common apex.
# Bottom rim: p0..p6 (7 vertices), common apex at p7.
p0 = m.vertex(0.0, 0.0, 0.0)    # 0
p1 = m.vertex(1.0, 0.0, 0.0)    # 1
p2 = m.vertex(2.0, 0.0, 0.0)    # 2
p3 = m.vertex(3.0, 0.0, 0.0)    # 3
p4 = m.vertex(4.0, 0.0, 0.0)    # 4
p5 = m.vertex(5.0, 0.0, 0.0)    # 5
p6 = m.vertex(6.0, 0.0, 0.0)    # 6
ap = m.vertex(3.0, 3.0, 0.0)    # 7 — shared apex

# 6 fan triangles: each pair shares the edge to the apex.
f0 = m.triangle(p0, p1, ap)   # face 0: seed; shares (p1,ap) with f1
f1 = m.triangle(p1, p2, ap)   # face 1: shares (p1,ap) with f0, (p2,ap) with f2
f2 = m.triangle(p2, p3, ap)   # face 2: shares (p2,ap) with f1, (p3,ap) with f3
f3 = m.triangle(p3, p4, ap)   # face 3: shares (p3,ap) with f2, (p4,ap) with f4
f4 = m.triangle(p4, p5, ap)   # face 4: shares (p4,ap) with f3, (p5,ap) with f5
f5 = m.triangle(p5, p6, ap)   # face 5: shares (p5,ap) with f4

# Each interior apex-edge is shared by exactly 2 fan triangles.
m.assert_edge_shared(p1, ap, 2)   # f0 and f1
m.assert_edge_shared(p2, ap, 2)   # f1 and f2
m.assert_edge_shared(p3, ap, 2)   # f2 and f3
m.assert_edge_shared(p4, ap, 2)   # f3 and f4
m.assert_edge_shared(p5, ap, 2)   # f4 and f5

# Component B: isolated triangle far from the fan.
q0 = m.vertex(50.0, 0.0, 0.0)   # 8
q1 = m.vertex(51.0, 0.0, 0.0)   # 9
q2 = m.vertex(50.5, 1.0, 0.0)   # 10
iso = m.triangle(q0, q1, q2)   # face 6: second CC — outer loop seeds new BFS here

# Component B is unreachable from component A.
m.assert_triangle_not_reachable_from(iso, f0)
