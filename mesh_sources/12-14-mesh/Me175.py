"""Me175 — orient_same_orientation_edge: edge traversed in same direction by two triangles.

Catalog claim: two adjacent triangles traverse their shared edge in the same
direction (i1→i2 from both), meaning they are wound the same way around the
edge — a same-orientation conflict. Branch 6 (*same_orientation_edge*) of the
orient algorithm fires when the edge lookup `it_same_orient` finds a neighbor
in the "same-direction" edge map for edge (i1→i2).

Geometric signature: t0=(v0,v1,v2) and t1=(v0,v1,v3). Both traverse edge
v0→v1 in the same directed sense. t0 has a +Z normal; t1 (with v3 below the
plane) has a -Z normal. The same-direction traversal of (v0,v1) is what
Branch 6 detects: the edge map entry for directed edge (v0→v1) has two
owners, signaling a same-orientation pair.

Defect carrier: the directed edge (v0,v1) appears in both t0 and t1. Both
triangles traverse it in the same direction — the hallmark of inconsistent
winding when two faces share an undirected edge.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me175",
             title="orient same_orientation_edge: shared edge traversed in same direction by both triangles",
             defect_class="inconsistent_winding")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — above
v3 = m.vertex(0.5,-1.0, 0.0)   # 3 — below

# Both triangles start with directed edge v0→v1 (same orientation on shared edge).
t0 = m.triangle(v0, v1, v2)   # v0→v1→v2, normal +Z
t1 = m.triangle(v0, v1, v3)   # v0→v1→v3, normal -Z (same directed shared edge → defect)
# t1 normal: (v1-v0)×(v3-v0) = (1,0,0)×(0.5,-1,0) = (0,0,-1) → -Z ✓

# Canonical (undirected) edge is shared by both triangles.
m.assert_edge_shared(v0, v1, 2)

# Antiparallel normals confirm same-orientation-edge defect.
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)
