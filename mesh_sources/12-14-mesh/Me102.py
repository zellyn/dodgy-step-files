"""Me102 — unlink_triangle_v3_boundary_non_manifold: v3 is on the boundary but
both its incident edges are non-boundary.

MeshFix `Basic_TMesh.unlinkTriangle` Branch 3 (*vertex_manifold_check_v3*):
mirrors Branches 1 and 2 but for the *third* vertex (v3 in MeshFix notation,
which is the apex opposite the base edge). v3->isOnBoundary() returns true
(open link ring) yet both edges incident on v3 in the target triangle are
interior (shared by two triangles each), signalling a non-manifold singularity.

Geometry — apex-non-manifold pyramid strip:
  v0=(0,0,0), v1=(2,0,0)  — base of target triangle t0
  v2=(1,1,0)  — apex = "v3" in MeshFix (third vertex); on boundary, both edges non-boundary

  t0 = (v0, v1, v2)   ← target; v2 is the apex (third vertex)
  t1 = (v0, v2, v3c)  — shares edge (v0,v2) with t0
  t2 = (v1, v3d, v2)  — shares edge (v1,v2) with t0
  t3 = (v0, v3c, v3d) — closes the bottom loop but leaves gap at v2

  v3c=(0,2,0), v3d=(2,2,0) — upper outer ring vertices

  v2's fan: t0→t1 (via edge v0,v2) and t0→t2 (via edge v1,v2); the ring
  is open at the top (no edge v3c↔v3d in the fan), so v2 isOnBoundary.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me102",
             title="unlink_triangle_v3_boundary_non_manifold: apex vertex on boundary but both incident edges non-boundary",
             defect_class="unlink_vertex_manifold_v3")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — base left
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — base right
v2 = m.vertex(1.0, 1.0, 0.0)   # 2 — apex / third vertex: on boundary, both edges non-boundary
v3c = m.vertex(0.0, 2.0, 0.0)  # 3 — upper left outer
v3d = m.vertex(2.0, 2.0, 0.0)  # 4 — upper right outer

# Target triangle; v2 is the third (apex) vertex.
t0 = m.triangle(v0, v1, v2)    # 0 — target

# Triangles sharing t0's edges at v2.
t1 = m.triangle(v0, v2, v3c)   # 1 — shares edge (v0,v2) with t0
t2 = m.triangle(v1, v3d, v2)   # 2 — shares edge (v1,v2) with t0
t3 = m.triangle(v0, v3c, v3d)  # 3 — bottom closure (keeps v0 interior or boundary)

# Both edges of t0 incident on apex v2 are non-boundary (interior).
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v1, v2, 2)   # shared by t0 and t2

# t0's base edge (v0,v1) is a boundary edge.
m.assert_edge_shared(v0, v1, 1)   # boundary

# v2's ring is open: gap from v3c to v3d (no closing edge).
m.assert_edge_shared(v0, v3c, 2)  # interior: shared by t1 and t3 (v0,v3c is in both)
m.assert_edge_shared(v1, v3d, 1)  # boundary confirming v2's link is open
m.assert_edge_shared(v3c, v3d, 1) # boundary gap (no triangle closing v3c↔v3d at v2)
