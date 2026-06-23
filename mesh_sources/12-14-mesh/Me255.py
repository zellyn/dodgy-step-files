"""Me255 — openToDisk_boundary_edge_exists: spanning tree processes a boundary edge (Branch 6).

MeshFix `Basic_TMesh.openToDisk` Branch 6 (*boundary_edge_exists*) @ line 1825:
  've->numels()' — vertex has pending boundary edges in traversal; process next one.

After finding the leaf root vertex, openToDisk traverses boundary edges in a
spanning-tree fashion. Branch 6 fires for each step where the current vertex still
has pending (unvisited) boundary edges in its adjacency list. The algorithm marks
each boundary edge (MARK_BIT) and moves to the opposite vertex.

Geometry: a single open quadrilateral strip with 2 triangles. The spanning tree
traversal starts from one endpoint and traverses the boundary loop one edge at a
time. Each step that finds a pending boundary edge triggers Branch 6.

Boundary loop: v0 — v1 — v3 — v2 — v0 (four boundary edges).
Starting at v0, traverse: (v0-v1) → move to v1; (v1-v3) → move to v3;
(v3-v2) → move to v2; finally (v2-v0) closes the cycle (Branch 7).
Each of the first three traversal steps fires Branch 6.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me255",
             title="openToDisk_boundary_edge_exists: spanning tree traverses boundary edges (Branch 6)",
             defect_class="open_to_disk_boundary_edge")

# 2-triangle quad strip (same geometry as Me228).
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(1.5, 1.0, 0.0)   # 3

t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v1, v3, v2)   # 1

# Interior edge: shared by both triangles.
m.assert_edge_shared(v1, v2, 2)

# Boundary edges: traversed one-by-one during Branch 6 spanning tree walk.
m.assert_edge_shared(v0, v1, 1)   # traversal step 1: Branch 6 fires
m.assert_edge_shared(v1, v3, 1)   # traversal step 2: Branch 6 fires
m.assert_edge_shared(v2, v3, 1)   # traversal step 3: Branch 6 fires
m.assert_edge_shared(v0, v2, 1)   # traversal step 4: cycle closes (Branch 7)

# Boundary loop: 4-edge loop around the strip.
m.assert_hole_boundary([v0, v1, v3, v2])
