"""Me161 — stitch_start_triangle_t1: starting triangle (t0) selected via t1 branch.

MeshFix `Edge.stitch` Branch 2 (*STITCH_START_TRIANGLE*) @ line 371:
  't0 = (t1 != NULL) ? (t1) : (t2)'
  After confirming the edge is on the boundary, stitch selects the starting
  triangle for the boundary walk. If t1 is non-NULL, t0 = t1; otherwise t0 = t2.
  Branch 2 covers the t1-non-NULL case.

Defect pattern: a boundary edge whose t1 field (first triangle slot) is occupied
by a single incident triangle. The ternary selects t1 as the walk starting point.
This is a topology fixture: the defect is a boundary gap between two open patches
that share coincident boundary edges but are not yet stitched together.

Geometry: three-triangle open strip — two patches sharing a coincident boundary.
  Patch A: t0=(v0,v1,v2) with boundary edge (v0,v1).
  Patch B: t1=(v3,v4,v5) with boundary edge (v3,v4) geometrically coincident
           to (v0,v1) but stored as separate vertices (gap not yet merged).
  The boundary edge on Patch A has t1 occupied (t0 is the incident triangle);
  t2 is NULL (boundary side). stitch uses t1 branch to start the boundary walk.

For the oracle, we assert that edge (v0,v1) and edge (v3,v4) are each incident
on exactly one triangle — confirming both are boundary edges (unstitched gap).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me161",
             title="stitch_start_triangle_t1: boundary edge with t1 occupied selects t1 as walk start",
             defect_class="stitch_boundary_gap_t1_branch")

# Patch A: left open triangle
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

# Patch B: right open triangle — coincident boundary but separate vertices
v3 = m.vertex(0.0, 0.0, 0.0)   # 3 — same position as v0 (unstitched)
v4 = m.vertex(1.0, 0.0, 0.0)   # 4 — same position as v1 (unstitched)
v5 = m.vertex(0.5, -1.0, 0.0)  # 5 — below the x-axis

t0 = m.triangle(v0, v1, v2)    # 0 — Patch A
t1 = m.triangle(v3, v4, v5)    # 1 — Patch B

# Both (v0,v1) and (v3,v4) are boundary edges — each incident on one triangle.
m.assert_edge_shared(v0, v1, 1)  # Patch A boundary; t1 occupied → t0 chosen as walk start
m.assert_edge_shared(v3, v4, 1)  # Patch B boundary — coincident target edge

# Near-coincident vertex pairs confirm the geometry of the unstitched gap.
m.assert_vertex_pair_distance_lt(v0, v3, 1e-9)
m.assert_vertex_pair_distance_lt(v1, v4, 1e-9)
