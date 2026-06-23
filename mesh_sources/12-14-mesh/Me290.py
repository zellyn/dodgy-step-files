"""Me290 — connected_components iteration_construct: outer-loop visits all faces.

Catalog claim: CGAL PMP.connected_components Branch 1 @ line 224
(*Iteration_construct*): the outer for-loop iterates over every face in
the mesh. A mesh with three disconnected single-triangle components forces
the outer loop to start a new BFS from each unhandled face. Without this
outer iteration construct, only the first component would be labelled.

Geometric signature: three isolated triangles, each far from the others,
sharing no edges or vertices. PMP.connected_components must run its outer
for-loop to completion to assign three distinct CC labels (0, 1, 2). The
oracle checks that no triangle is reachable from either of the others.

Source: CGAL PMP.connected_components Branch 1 @ line 224
(*Iteration_construct*) — outer `for` loop over all faces; visits every
face in the mesh to seed new BFS traversals for unhandled components.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me290",
             title="connected_components iteration_construct: outer for-loop visits three isolated triangle components",
             defect_class="disconnected_components")

# Component A: triangle near origin (CC label 0).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
t0 = m.triangle(v0, v1, v2)

# Component B: triangle 50 units away (CC label 1).
v3 = m.vertex(50.0, 0.0, 0.0)
v4 = m.vertex(51.0, 0.0, 0.0)
v5 = m.vertex(50.5, 1.0, 0.0)
t1 = m.triangle(v3, v4, v5)

# Component C: triangle 100 units away (CC label 2).
v6 = m.vertex(100.0, 0.0, 0.0)
v7 = m.vertex(101.0, 0.0, 0.0)
v8 = m.vertex(100.5, 1.0, 0.0)
t2 = m.triangle(v6, v7, v8)

# Each component is unreachable from the others — three separate BFS seeds.
m.assert_triangle_not_reachable_from(t1, t0)
m.assert_triangle_not_reachable_from(t2, t0)
m.assert_triangle_not_reachable_from(t2, t1)
