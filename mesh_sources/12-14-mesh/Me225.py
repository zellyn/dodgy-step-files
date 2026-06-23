"""Me225 — eulerUpdate_boundary_exists: hasBoundary flag gates boundary-loop phase (Branch 6).

MeshFix `Basic_TMesh.eulerUpdate` Branch 6 (*boundary_exists*) @ line 1771:
  'if (hasBoundary)' — mesh has at least one boundary; process boundary vertex loops.

After the edge-scan phase sets hasBoundary=true (Branch 5), eulerUpdate checks
the flag before entering the boundary-loop traversal. Branch 6 is the condition
gate: if hasBoundary is true, walk all boundary vertices and count loops (Branch 7).
Without an open boundary this branch is never taken.

Geometry: a triangulated disk (fan of three triangles around a hub vertex)
with an open boundary ring. Every spoke edge is interior; the outer rim edges
are boundary (n=1). hasBoundary is set true, gating the n_boundaries count.

  hub = v0 = (0,0,0)
  rim: v1, v2, v3, v4 (four rim vertices)
  Triangles: (v0,v1,v2), (v0,v2,v3), (v0,v3,v4)
  Outer boundary loop: v1-v2-v3-v4 with open gap v4→v1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me225",
             title="eulerUpdate_boundary_exists: hasBoundary=true gates boundary-loop processing",
             defect_class="open_boundary")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — hub
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(-0.5, 1.0, 0.0)  # 3
v4 = m.vertex(-1.0, 0.0, 0.0)  # 4

t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v0, v2, v3)   # 1
t2 = m.triangle(v0, v3, v4)   # 2

# Spoke edges — interior (shared by adjacent fan triangles).
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)

# Outer rim boundary edges (n=1).
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)

# Open spoke edges (n=1) — the gap spokes.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v4, 1)

# The open boundary: outer rim + gap spokes form one boundary loop.
m.assert_hole_boundary([v1, v2, v3, v4, v0])
