"""Me270 — autorefine_triangle_soup: no-intersections trivial case (Branch 1).

CGAL PMP `autorefine_impl::autorefine_triangle_soup` Branch 1 @ line 1040:
  'si_pairs.empty()' — when the bbox-based intersection query returns zero pairs,
  the function copies the input triangles verbatim and returns immediately without
  entering the refinement pipeline.

This is the trivial short-circuit: a clean triangle soup with no self-intersecting
pairs causes si_pairs to be empty, so Branch 1 is taken and the output is identical
to the input (number_of_output_triangles == number_of_input_triangles).

Geometry: two well-separated non-intersecting triangles. No SI pair exists; the
AABB / bbox query returns an empty si_pairs collection. The function copies the
triangles verbatim.

Defect class: autorefine_no_si — a soup that requires no splitting at all because
all triangles are already non-self-intersecting.

Keywords: si_pairs.empty, number_of_output_triangles, trivial copy.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me270",
             title="autorefine_triangle_soup no-SI trivial case: si_pairs.empty() → verbatim copy",
             defect_class="autorefine_no_si")

# Triangle 0: left panel, z=0 plane.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

# Triangle 1: right panel, well separated, z=0 plane.
v3 = m.vertex(5.0, 0.0, 0.0)   # 3
v4 = m.vertex(6.0, 0.0, 0.0)   # 4
v5 = m.vertex(5.5, 1.0, 0.0)   # 5

t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v3, v4, v5)   # 1

# Verify the two triangles do NOT intersect — si_pairs will be empty.
m.assert_triangles_do_not_intersect(t0, t1)

# Each edge is incident on exactly 1 triangle (open/soup mesh, no shared edges).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)
