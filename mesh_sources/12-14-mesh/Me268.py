"""Me268 — range_with_face_set_whole_component_selected: all non-border faces marked for removal.

Catalog claim: CGAL PMP.remove_degenerate_edges.range_with_face_set Branch 9 @ line 1704
(*whole_connected_component_selected*): when collecting faces around the degenerate edge,
the algorithm finds that ALL non-border faces are marked. The border set (border.empty())
is empty because there are no remaining boundary edges separating marked from unmarked
faces. Removing the entire component would be wrong, so the algorithm skips and marks
all_removed=false.

Geometric signature: a single isolated triangle (single-triangle connected component) that
contains the degenerate edge. When this triangle is the ONLY face in the component, marking
the face for removal marks the ENTIRE component — border.empty() is true because there
is no surrounding mesh context. The algorithm detects this and skips.

Configuration: two disconnected components:
  A: a small patch (triangles 0-2) — the normal component
  B: a single triangle (triangle 3) containing a near-degenerate edge — the whole-component case
  When CGAL processes triangle 3, it is the entire connected component; marking it for
  removal means border=empty → skip.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me268",
             title="range_with_face_set whole_component_selected: single-triangle component with degenerate edge → border.empty() → skip",
             defect_class="degenerate_edge")

# Component A: a small triangulated patch (3 triangles), no degenerate edges.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)

t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v0, v2, v3)   # 1
t2 = m.triangle(v1, v3, v2)   # 2 — wait this adds edge(1,3) shared with t1... ok for component A

# Component B: single isolated triangle with a degenerate near-zero-length edge.
# Far from component A.
v4 = m.vertex(10.0,        0.0, 0.0)   # b0
v5 = m.vertex(10.0+1e-10,  0.0, 0.0)   # b1 ≈ b0: degenerate edge
v6 = m.vertex(10.5,        1.0, 0.0)   # b2: apex

t3 = m.triangle(v4, v5, v6)   # 3: the lone triangle — entire component B

# Component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t3, t0)

# The degenerate edge (v4,v5) is a boundary edge (only in t3, n=1).
m.assert_edge_shared(v4, v5, 1)

# v4 and v5 are nearly coincident.
m.assert_vertex_pair_distance_lt(v4, v5, 1e-9)

# The near-degenerate triangle has near-zero area.
m.assert_triangle_area_lt(t3, 1e-8)
