"""Me1085 — remove_degenerate_faces degenerate_edge_in_face: needle triangle with zero-length edge; is_degenerate_edge fires before face removal (Branch 6).

CGAL PMP `PMP.remove_degenerate_faces` Branch 6 (*degenerate_edge_in_face*) @ line 2170:
  'if (is_degenerate_edge(h, tmesh, vpm, gt)) { ... remove_degenerate_edges ... }'
  — when processing a degenerate face, the algorithm checks each halfedge h of the face
  for a zero-length edge. If is_degenerate_edge returns true, remove_degenerate_edges is
  called first to collapse the zero-length edge before attempting the face-removal Euler
  operators. This prevents illegal topology operations on faces with degenerate edges.

Defect pattern: a needle triangle where two vertices share exactly the same coordinates,
  creating a zero-length edge. The triangle degenerates to a line segment.
  The mesh also includes a larger non-degenerate triangle for geometric context.

Geometry:
  n0=(0,0,0), n1=(3,0,0), n2=(3,0,0) — n1 and n2 at same position → zero-length edge
  n3=(1.5,0,0) — collapses triangle to segment from (0,0,0) to (3,0,0)
  t0=(n0,n1,n2): zero-length edge (n1,n2); area=0 → degenerate face with degenerate edge
  t1=(c0,c1,c2): clean control triangle far from defect; area > 0
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1085",
    title="remove_degenerate_faces degenerate_edge_in_face: needle triangle n0-n1-n2 with zero-length edge (n1==n2 at (3,0,0)); is_degenerate_edge fires → remove_degenerate_edges called (Branch 6)",
    defect_class="degenerate_triangle",
)

# Needle triangle: n1 and n2 share coordinates → zero-length edge.
n0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left endpoint
n1 = m.vertex(3.0, 0.0, 0.0)  # 1 — right endpoint; coincides with n2
n2 = m.vertex(3.0, 0.0, 0.0)  # 2 — same as n1 (zero-length edge)

t0 = m.triangle(n0, n1, n2)   # 0: needle — zero-length edge (n1,n2); area=0

# Clean non-degenerate control triangle.
c0 = m.vertex(5.0, 0.0, 0.0)  # 3
c1 = m.vertex(6.0, 0.0, 0.0)  # 4
c2 = m.vertex(5.5, 1.0, 0.0)  # 5 — apex gives positive area
t1 = m.triangle(c0, c1, c2)   # 1: clean; area = 0.5

# Needle triangle: zero-length edge and zero area.
m.assert_vertex_pair_distance_lt(n1, n2, 1e-12)  # zero-length degenerate edge (n1,n2)
m.assert_triangle_area_lt(t0, 1e-12)              # face collapses to line segment

# Boundary edges of the needle triangle (no sharing with any other face).
m.assert_edge_shared(n0, n1, 1)   # boundary
m.assert_edge_shared(n1, n2, 1)   # the zero-length degenerate edge; is_degenerate_edge fires here
m.assert_edge_shared(n0, n2, 1)   # boundary
