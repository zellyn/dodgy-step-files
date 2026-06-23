"""Me100 — unlink_triangle_v1_boundary_non_manifold: v1 is on the boundary but
both its incident edges (e1 and e2 — the two edges of the target triangle
incident on v1) are shared by a second triangle (non-boundary).

MeshFix `Basic_TMesh.unlinkTriangle` Branch 1 (*vertex_manifold_check_v1*):
'if (v1->isOnBoundary())' — v1 is flagged as a boundary vertex, yet both edges
e1 and e2 incident on v1 inside the target triangle are each shared with another
triangle (shared by 2, not on the mesh boundary). This inconsistency means v1 is
a non-manifold singularity: it lies on the "boundary" according to MeshFix's
bookkeeping but topologically all edges leaving it are interior. Unlinking the
triangle would leave v1 in an invalid state unless it is duplicated first.

Geometry:
  Five-vertex fan where v1 sits at the center of a star:
    v0=(0,0,0)  — interior (only in target triangle t0)
    v1=(1,0,0)  — center: in t0 AND t1 AND t2; BOTH edges (v0,v1) and (v1,v2)
                   are shared with another triangle so they are non-boundary,
                   yet v1 appears to be "on the boundary" per MeshFix because
                   its link does not form a closed ring.
    v2=(2,0,0)  — shared between t0 and t1
    v3=(1,1,0)  — shared between t0 and t2
    v4=(2,1,0)  — outer vertex in t1
    v5=(0,1,0)  — outer vertex in t2

  Triangles:
    t0 = (v0, v1, v2) ← target triangle to unlink (v1 is the "v1 corner")
    t1 = (v1, v4, v2)  — shares edge (v1,v2) with t0
    t2 = (v0, v3, v1)  — shares edge (v0,v1) with t0
    t3 = (v1, v3, v4)  — closes the ring around v1 at the top

After adding t3 the ring at v1 is [v0,v2,v4,v3] and is NOT closed back to v0
(edge (v3,v0) is absent), so v1 is on the boundary — yet both t0-edges at v1
are interior (shared with t1 and t2 respectively), hitting Branch 1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me100",
             title="unlink_triangle_v1_boundary_non_manifold: v1 on boundary but both incident edges non-boundary",
             defect_class="unlink_vertex_manifold_v1")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — only in t0 and t2
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — center vertex: in t0, t1, t2, t3
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — in t0 and t1
v3 = m.vertex(1.0, 1.0, 0.0)   # 3 — in t2 and t3
v4 = m.vertex(2.0, 1.0, 0.0)   # 4 — in t1 and t3

# Target triangle (t0): v1 is the first vertex.
t0 = m.triangle(v0, v1, v2)   # 0 — target; edges (v0,v1) and (v1,v2) are non-boundary

# Two triangles sharing t0's edges at v1.
t1 = m.triangle(v1, v4, v2)   # 1 — shares edge (v1,v2) with t0
t2 = m.triangle(v0, v3, v1)   # 2 — shares edge (v0,v1) with t0
t3 = m.triangle(v1, v3, v4)   # 3 — closes upper ring at v1 (t2→t3 chain)

# Both edges incident on v1 inside t0 are shared (non-boundary).
m.assert_edge_shared(v1, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t2

# Edge (v0,v2) is the third edge of t0 — it is a boundary edge (in t0 only).
m.assert_edge_shared(v0, v2, 1)   # boundary of the mesh

# v1's link is open at (v3,v0): top gap confirms v1 is on the boundary.
m.assert_edge_shared(v0, v3, 1)   # open boundary gap: confirms v1 link not closed
