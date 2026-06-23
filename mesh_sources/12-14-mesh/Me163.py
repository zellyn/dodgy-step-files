"""Me163 — stitch_boundary_walk_v2: boundary walk from v1 fails, retries from v2.

MeshFix `Edge.stitch` Branch 4 (*BOUNDARY_WALK_V2*) @ line 375:
  'v0 = ((v0 == v1) ? (v2) : (NULL))'
  If the boundary walk starting from v1 reaches a dead end without finding a
  coincident candidate edge, stitch resets the walk to start from v2 (the other
  endpoint of the stitch edge). Branch 4 covers this v2-retry fallback.

Defect pattern: a three-triangle open strip where the coincident boundary edge
is only reachable via the v2 endpoint (not v1). The v1 walk dead-ends at a
T-junction where no coincident edge exists in that direction.

Geometry: asymmetric open strip — boundary gap only accessible from v2 side.
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0) — Patch A base triangle t0
  v3=(1,1,0), v4=(0,2,0) — Patch A extension t1 sharing (v2,v3)
  Stitch target edge: (v1,v2) on t0, boundary.
  Candidate: (v5,v6) near (v2,v1) on Patch B, only reachable from v2.

The v1-side walk follows boundary edges away from the gap; the v2-side walk
finds the geometrically coincident edge on Patch B.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me163",
             title="stitch_boundary_walk_v2: v1 walk fails, boundary walk retries from v2 endpoint to find coincident edge",
             defect_class="stitch_boundary_walk_v2_retry")

# Patch A: base triangle with target boundary edge (v1,v2)
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — right endpoint of stitch edge
v2 = m.vertex(1.0, 1.0, 0.0)   # 2 — apex endpoint of stitch edge

# Patch A extension connected via v0 — extends away from v1 (dead-end direction)
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3 — outer left vertex

# Patch B: coincident boundary on opposite side (near v2→v1 direction)
v4 = m.vertex(1.0, 1.0, 0.0)   # 4 — same position as v2 (unstitched)
v5 = m.vertex(2.0, 0.0, 0.0)   # 5 — same position as v1 (unstitched)
v6 = m.vertex(1.5, 2.0, 0.0)   # 6 — outer vertex of patch B

t0 = m.triangle(v0, v1, v2)    # 0 — Patch A; stitch edge (v1,v2) is boundary
t1 = m.triangle(v0, v3, v2)    # 1 — Patch A extension; shares (v0,v2) with t0 — dead end from v1
t2 = m.triangle(v4, v5, v6)    # 2 — Patch B; edge (v4,v5) coincident to (v2,v1)

# Target stitch edge (v1,v2) is a boundary edge (only t0 incident).
m.assert_edge_shared(v1, v2, 1)  # walk starts here; v1 walk dead-ends

# Shared edge between t0 and t1 is interior.
m.assert_edge_shared(v0, v2, 2)  # interior — blocks v1-side walk continuation

# Candidate boundary edge on Patch B is coincident to (v2,v1).
m.assert_edge_shared(v4, v5, 1)

# Near-coincident pairs confirm the unstitched gap.
m.assert_vertex_pair_distance_lt(v2, v4, 1e-9)
m.assert_vertex_pair_distance_lt(v1, v5, 1e-9)
