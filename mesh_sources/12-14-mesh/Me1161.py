"""Me1161 — triangulate_and_refine_hole.main output_iterator_choice face:
  face_output_iterator parameter presence/absence; triangular hole bordered
  by 3 hat triangles; Emptyset_iterator discards face output (Branch 1).

CGAL PMP `triangulate_and_refine_hole.main` Branch 1 (*output_iterator_choice*)
  @ line 381:
  'face_out = choose_parameter(get_parameter(np, internal_np::face_output_iterator),
    Emptyset_iterator());' —
  triangulate_and_refine_hole checks whether the caller supplied a
  face_output_iterator named parameter. If absent, it substitutes
  Emptyset_iterator which silently discards all new face descriptors. Branch 1
  fires when this parameter lookup is evaluated.

Defect pattern: a triangular hole bordered by three hat-triangles. No caller-
  supplied face_output_iterator: the function resolves to Emptyset_iterator.
  New fill-faces are triangulated but their descriptors are discarded. The hole
  boundary has 3 edges; 3 surrounding faces each share one boundary edge.

Geometry:
  Hat ring: h0=(0,0,0), h1=(2,0,0), h2=(1,1.73,0),
            h3=(1,-1,0), h4=(3,1,0), h5=(-1,1,0)
  t0=(h0,h3,h1), t1=(h1,h4,h2), t2=(h2,h5,h0) — three hat triangles.
  Hole boundary: h0→h1→h2→h0 (3 edges each n=1).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1161",
    title="triangulate_and_refine_hole.main output_iterator_choice face: Emptyset_iterator substituted when face_output_iterator absent; 3-edge triangular hole (Branch 1)",
    defect_class="boundary_hole",
)

# Hole boundary vertices (form the triangle to be filled).
h0 = m.vertex(0.0,  0.0,    0.0)    # 0 — hole corner A
h1 = m.vertex(2.0,  0.0,    0.0)    # 1 — hole corner B
h2 = m.vertex(1.0,  1.73,   0.0)    # 2 — hole corner C

# Hat triangle vertices (outside the hole).
h3 = m.vertex(1.0,  -1.0,   0.0)    # 3 — outer vertex of t0
h4 = m.vertex(3.0,  1.0,    0.0)    # 4 — outer vertex of t1
h5 = m.vertex(-1.0, 1.0,    0.0)    # 5 — outer vertex of t2

# Three hat triangles surrounding the hole.
t0 = m.triangle(h0, h3, h1)  # 0: bottom hat
t1 = m.triangle(h1, h4, h2)  # 1: right hat
t2 = m.triangle(h2, h5, h0)  # 2: left hat

# Interior hole boundary edges — each shared by exactly 1 hat triangle.
m.assert_edge_shared(h0, h1, 1)  # bottom hole edge
m.assert_edge_shared(h1, h2, 1)  # right hole edge
m.assert_edge_shared(h0, h2, 1)  # left hole edge

# Outer hat edges (each n=1 on boundary).
m.assert_edge_shared(h0, h3, 1)
m.assert_edge_shared(h1, h3, 1)
m.assert_edge_shared(h1, h4, 1)
m.assert_edge_shared(h2, h4, 1)
m.assert_edge_shared(h2, h5, 1)
m.assert_edge_shared(h0, h5, 1)

# Hole boundary loop: h0→h1→h2→h0.
m.assert_hole_boundary([h0, h1, h2])

# Open mesh with boundary: V=6, E=9, F=3, chi=0 (disk-like with hole).
m.assert_euler_characteristic(6, 9, 3, 0)
