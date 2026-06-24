"""Me1162 — triangulate_and_refine_hole.main output_iterator_choice vertex:
  vertex_output_iterator parameter presence/absence; Emptyset_iterator
  discards new vertex output from refine step (Branch 2).

CGAL PMP `triangulate_and_refine_hole.main` Branch 2 (*output_iterator_choice*)
  @ line 387:
  'vertex_out = choose_parameter(get_parameter(np, internal_np::vertex_output_iterator),
    Emptyset_iterator());' —
  triangulate_and_refine_hole checks whether the caller supplied a
  vertex_output_iterator named parameter. If absent, it substitutes
  Emptyset_iterator which silently discards all new vertex descriptors created
  during the refinement step. Branch 2 fires when this parameter lookup is
  evaluated.

Defect pattern: a quadrilateral hole bordered by four hat-triangles. No caller-
  supplied vertex_output_iterator: the function resolves to Emptyset_iterator.
  Refinement may insert Steiner vertices but their descriptors are discarded.
  The hole boundary has 4 edges.

Geometry:
  Hole corners: q0=(0,0,0), q1=(2,0,0), q2=(2,2,0), q3=(0,2,0)
  Outer hat vertices: q4=(1,-1,0), q5=(3,1,0), q6=(1,3,0), q7=(-1,1,0)
  t0=(q0,q4,q1), t1=(q1,q5,q2), t2=(q2,q6,q3), t3=(q3,q7,q0).
  Hole boundary: q0→q1→q2→q3→q0 (4 edges each n=1).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1162",
    title="triangulate_and_refine_hole.main output_iterator_choice vertex: Emptyset_iterator substituted when vertex_output_iterator absent; 4-edge quad hole (Branch 2)",
    defect_class="boundary_hole",
)

# Hole boundary vertices.
q0 = m.vertex(0.0,  0.0,  0.0)    # 0 — SW corner
q1 = m.vertex(2.0,  0.0,  0.0)    # 1 — SE corner
q2 = m.vertex(2.0,  2.0,  0.0)    # 2 — NE corner
q3 = m.vertex(0.0,  2.0,  0.0)    # 3 — NW corner

# Outer hat vertices.
q4 = m.vertex(1.0,  -1.0, 0.0)    # 4 — south hat
q5 = m.vertex(3.0,  1.0,  0.0)    # 5 — east hat
q6 = m.vertex(1.0,  3.0,  0.0)    # 6 — north hat
q7 = m.vertex(-1.0, 1.0,  0.0)    # 7 — west hat

# Four hat triangles surrounding the quad hole.
t0 = m.triangle(q0, q4, q1)  # 0: south hat
t1 = m.triangle(q1, q5, q2)  # 1: east hat
t2 = m.triangle(q2, q6, q3)  # 2: north hat
t3 = m.triangle(q3, q7, q0)  # 3: west hat

# Hole boundary edges — each n=1.
m.assert_edge_shared(q0, q1, 1)
m.assert_edge_shared(q1, q2, 1)
m.assert_edge_shared(q2, q3, 1)
m.assert_edge_shared(q0, q3, 1)

# Outer hat boundary edges.
m.assert_edge_shared(q0, q4, 1)
m.assert_edge_shared(q1, q4, 1)
m.assert_edge_shared(q1, q5, 1)
m.assert_edge_shared(q2, q5, 1)
m.assert_edge_shared(q2, q6, 1)
m.assert_edge_shared(q3, q6, 1)
m.assert_edge_shared(q3, q7, 1)
m.assert_edge_shared(q0, q7, 1)

# Hole boundary loop: q0→q1→q2→q3→q0.
m.assert_hole_boundary([q0, q1, q2, q3])

# Open mesh with boundary: V=8, E=12, F=4, chi=0.
m.assert_euler_characteristic(8, 12, 4, 0)
