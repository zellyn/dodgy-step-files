"""Me137 — removeIfRedundant_opposite_vertices_side_check: opposite vertices of
the two triangles flanking the collapse edge are on opposite sides; edge swap
is performed before the vertex collapse.

MeshFix `Vertex.removeIfRedundant` Branch 8 @ line 372:
  'if (!exactSameSideOnPlane(...)) { e->swap() ... }'
  When the algorithm has identified the collapse edge (v_subject, v_neighbor),
  it checks whether the opposite vertices of the two triangles sharing this edge
  lie on the same side of the edge's plane. If they are on *opposite* sides,
  the current diagonal creates a concave (non-convex) quad that would invert on
  collapse, so MeshFix swaps the edge before proceeding.

Geometric signature: vertex v2 lies on the x-axis (DoubleFlat). The collapse
candidate edge is (v1, v2). Triangle t0=(v0,v1,v2) has opposite vertex v0=(0,2,0)
above the axis; triangle t1=(v1,v2,v3) has opposite vertex v3=(2,-1,0) below
the axis. The opposite vertices are on *opposite sides* of the y=0 plane along
the (v1,v2) direction, triggering the swap branch.

Geometry (z=0):
  v0=(0,2,0)   — far above: opposite vertex of t0 (positive y side)
  v1=(1,0,0)   — collapse edge start
  v2=(3,0,0)   — collapse edge end / DoubleFlat subject vertex
  v3=(2,-1,0)  — below axis: opposite vertex of t1 (negative y side)
  v4=(5,0,0)   — right neighbor to close the strip
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me137",
             title="removeIfRedundant_opposite_vertices_side_check: opposite vertices on opposite sides trigger edge swap before collapse",
             defect_class="redundant_vertex_removal_side_check_swap")

v0 = m.vertex(0.0, 2.0, 0.0)   # 0 — above axis (positive y)
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — collapse edge left vertex
v2 = m.vertex(3.0, 0.0, 0.0)   # 2 — DoubleFlat subject vertex (on x-axis)
v3 = m.vertex(2.0, -1.0, 0.0)  # 3 — below axis (negative y)
v4 = m.vertex(5.0, 0.0, 0.0)   # 4 — right anchor

t0 = m.triangle(v0, v1, v2)    # 0 — upper triangle, normal +z
t1 = m.triangle(v1, v2, v3)    # 1 — lower triangle, normal -z (flipped!)
t2 = m.triangle(v2, v3, v4)    # 2 — lower right close

# t0 and t1 share edge (v1,v2). t0 traverses v1→v2; t1 also traverses v1→v2
# (same direction) → inconsistent winding (both normals in same winding, but
# their normals point opposite ways because v0 is above and v3 is below).
#
# t0 normal: (v1-v0)×(v2-v0) = (1,-2,0)×(3,-2,0) = (0,0,1·(-2)-(-2)·3) = (0,0,4) → +z
# t1 normal: (v2-v1)×(v3-v1) = (2,0,0)×(1,-1,0) = (0,0,-2) → -z
# Opposite normals → inconsistent winding.
m.assert_adjacent_triangles_inconsistent_winding(0, 1)

# Edge (v1,v2): shared by t0 and t1 — this is the collapse candidate edge.
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v2, v3, 2)   # shared by t1 and t2
m.assert_edge_shared(v0, v1, 1)   # boundary
m.assert_edge_shared(v2, v4, 1)   # boundary
