"""Me279 — autorefine_triangle_soup: on_same_edge skip in segment branch (Branch 5b).

CGAL PMP `autorefine_impl::autorefine_triangle_soup` Branch 5 (sub-branch) @ line 1136:
  'on_same_edge' check — inside case 2 (two-point intersection), before calling
  segments.emplace_back, the code tests whether the two intersection points lie on
  a shared edge between the two triangles. If they do, no new segment is added
  (the shared edge is already manifold and needs no refinement).

This is the "negative" of Me274: instead of a free crossing segment, the two
intersection points are exactly on the shared edge between the two triangles.
Both triangles share the edge (v1, v2) and the intersection segment lies along
that exact edge — so 'on_same_edge' is true and segments.emplace_back is NOT called.

Geometry: two triangles that share one full edge (v1-v2). They are not coplanar;
they fold along the shared edge like an open book. The intersection of the two
triangles is exactly the shared edge itself, so nbi==2 (two endpoints) but
on_same_edge==true and the segment is skipped.

Keywords: case 2:, on_same_edge, segments.emplace_back skip, shared-edge intersection.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me279",
             title="autorefine_triangle_soup segment branch on_same_edge skip: shared edge → no new segment",
             defect_class="autorefine_shared_edge_skip")

# Shared edge: v1-v2.
v0 = m.vertex( 0.0, -1.0,  0.0)  # 0 — t0's private vertex
v1 = m.vertex(-1.0,  0.0,  0.0)  # 1 — shared edge endpoint
v2 = m.vertex( 1.0,  0.0,  0.0)  # 2 — shared edge endpoint
v3 = m.vertex( 0.0,  1.0,  0.0)  # 3 — t1's private vertex

# Triangle 0: below the shared edge.
t0 = m.triangle(v0, v1, v2)   # 0

# Triangle 1: above the shared edge (folds along v1-v2 like an open book).
t1 = m.triangle(v3, v1, v2)   # 1

# The shared edge v1-v2 is incident on exactly 2 triangles.
m.assert_edge_shared(v1, v2, 2)

# The remaining edges are each boundary (incident on 1 triangle).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v3, v1, 1)
m.assert_edge_shared(v3, v2, 1)

# The two triangles share the edge v1-v2 but are coplanar (both in z=0).
# Their intersection is the shared edge — on_same_edge==true.
# In the oracle, two coplanar non-overlapping triangles sharing only an edge
# do not produce a positive-area intersection.
m.assert_triangles_do_not_intersect(t0, t1)
