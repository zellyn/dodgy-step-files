"""Me403 — detect_identical_mergeable_vertices consecutive_identical_collection: inner while loop runs for 3+ consecutive coincident halfedges (Branch 4).

CGAL PMP `PMP.internal.detect_identical_mergeable_vertices` Branch 4 (*consecutive_identical_collection*) @ line 175:
  'while(++i != nbv &&
         get(vpm, target(cycle_hedges[i], mesh)) == get(vpm, target(cycle_hedges[i-1], mesh)))
   { candidate_hedges_with_id.back().push_back(i); }'
  — after a two-element group is started (Branch 3), this inner while loop continues
  collecting halfedges whose target point is still identical. A third halfedge with the
  same target coordinate is pushed into the current group, extending it to size 3.

Defect pattern: five triangles (three "cell" triangles on the bottom and two "bridge"
  triangles on top) with a single boundary cycle containing THREE topologically-distinct
  vertices all at coordinate (1.0, 0.0, 0.0): q0, q1, q2 (indices 4, 5, 6). No two of
  the coincident vertices share any triangle. After sorting the boundary halfedges, the
  three coincident-target halfedges become consecutive. Branch 3 opens the group with
  {q0,q1}; Branch 4's inner while fires once to push q2, extending the group to size 3.

Geometry:
  Top row (distinct): p0=(0,1,0), p1=(2,1,0), p2=(4,1,0), p3=(6,1,0)
  Bottom (coincident): q0=q1=q2=(1,0,0) — three distinct index entries at same coord.

  t0=(p0,q0,p1): left cell   [uses bottom vertex q0]
  t1=(p1,q1,p2): middle cell [uses bottom vertex q1]
  t2=(p2,q2,p3): right cell  [uses bottom vertex q2]
  t3=(p0,p1,p2): left bridge [connects top of cells 0,1,2]
  t4=(p0,p2,p3): right bridge [connects top of cells 1,2,3]

  Interior edges (n=2): (p0,p1),(p1,p2),(p0,p2),(p2,p3).
  Boundary cycle: p0→q0→p1→q1→p2→q2→p3→p0.
  Euler: V=7, E=11, F=5, chi=1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me403",
    title="detect_identical_mergeable_vertices consecutive_identical_collection: q0==q1==q2 at (1,0,0), no two share a triangle; inner while extends group to size 3 (Branch 4)",
    defect_class="near_coincident_vertex",
)

# Top row — four distinct vertices.
p0 = m.vertex(0.0, 1.0, 0.0)  # 0
p1 = m.vertex(2.0, 1.0, 0.0)  # 1
p2 = m.vertex(4.0, 1.0, 0.0)  # 2
p3 = m.vertex(6.0, 1.0, 0.0)  # 3

# Bottom row — three coincident vertices (distinct indices, identical coordinates).
q0 = m.vertex(1.0, 0.0, 0.0)  # 4 — coincident with q1 and q2
q1 = m.vertex(1.0, 0.0, 0.0)  # 5 — coincident with q0 and q2
q2 = m.vertex(1.0, 0.0, 0.0)  # 6 — coincident with q0 and q1

# Three cell triangles — each uses one coincident bottom vertex.
t0 = m.triangle(p0, q0, p1)  # 0: left cell
t1 = m.triangle(p1, q1, p2)  # 1: middle cell
t2 = m.triangle(p2, q2, p3)  # 2: right cell

# Two bridge triangles — connect the cells across the top, no bottom vertices.
t3 = m.triangle(p0, p1, p2)  # 3: left bridge
t4 = m.triangle(p0, p2, p3)  # 4: right bridge

# Interior shared edges (n=2).
m.assert_edge_shared(p0, p1, 2)  # t0 and t3
m.assert_edge_shared(p1, p2, 2)  # t1 and t3
m.assert_edge_shared(p0, p2, 2)  # t3 and t4
m.assert_edge_shared(p2, p3, 2)  # t2 and t4

# Boundary edges (n=1) — the outer rim of the mesh.
m.assert_edge_shared(p0, q0, 1)  # t0 bottom-left
m.assert_edge_shared(p1, q0, 1)  # t0 bottom-right
m.assert_edge_shared(p1, q1, 1)  # t1 bottom-left
m.assert_edge_shared(p2, q1, 1)  # t1 bottom-right
m.assert_edge_shared(p2, q2, 1)  # t2 bottom-left
m.assert_edge_shared(p3, q2, 1)  # t2 bottom-right
m.assert_edge_shared(p0, p3, 1)  # t4 outer top-span

# Three coincident boundary vertices (all at (1,0,0)), none sharing a triangle.
# After sort, their halfedges are adjacent; Branch 3 starts group {q0,q1},
# Branch 4 extends it once to include q2 (group size → 3).
m.assert_vertex_pair_distance_lt(q0, q1, 1e-9)
m.assert_vertex_pair_distance_lt(q0, q2, 1e-9)
m.assert_vertex_pair_distance_lt(q1, q2, 1e-9)
m.assert_vertex_pair_no_shared_triangle(q0, q1)
m.assert_vertex_pair_no_shared_triangle(q0, q2)
m.assert_vertex_pair_no_shared_triangle(q1, q2)

# Euler: V=7, E=11, F=5, chi=1 (open disk).
m.assert_euler_characteristic(7, 11, 5, 1)
