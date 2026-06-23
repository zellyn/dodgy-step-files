"""Me170 — orient_polygon_scan: isolated second triangle found by scan loop.

Catalog claim: a mesh has two disconnected triangles with no shared edges.
The orient algorithm (Branch 1, *polygon_scan*) must increment polygon_index
past the first already-oriented polygon to find the second unoriented polygon.
Without Branch 1, the second triangle in an independent connected component
would never be reached.

Geometric signature: two separated, consistently CCW triangles with no shared
edge — one at z=0 (the first component, oriented as seed), one at z=5 (the
second component, reachable only by the polygon_scan loop).

Defect carrier: the second triangle t1 is the unoriented polygon that only the
scan loop (Branch 1) finds after t0 is oriented and the DFS stack empties.
Both triangles have CCW winding (+Z normals), so after orient they should be
globally consistent.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me170",
             title="orient polygon_scan: scan loop reaches isolated second component triangle",
             defect_class="inconsistent_winding")

# Component 1 — at z=0, CCW winding, +Z normal.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
t0 = m.triangle(v0, v1, v2)  # CCW, normal +Z

# Component 2 — at z=5, fully disconnected. CW winding so it is the defect
# that the scan must find and that orient would fix.
v3 = m.vertex(0.0, 0.0, 5.0)
v4 = m.vertex(1.0, 0.0, 5.0)
v5 = m.vertex(0.5, 1.0, 5.0)
t1 = m.triangle(v3, v5, v4)  # CW, normal -Z (the polygon_scan target)

# Component 2 is unreachable from component 1 by edge-walking (no shared edges).
m.assert_triangle_not_reachable_from(t1, t0)

# t1 has downward (-Z) normal confirming CW winding — it is the defect
# that polygon_scan must find and the orient BFS must fix.
m.assert_triangle_normal_z_negative(t1)

# t0 has upward (+Z) normal — the consistent seed.
# (No direct assertion for +Z, but inconsistent winding between the two
# components confirms they need cross-component orient.)
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)
