"""Me433 — checkAndRepair::forceNormalConsistence branch 4: BOUNDARY_EDGE_DETECTED.

MeshFix `checkAndRepair::forceNormalConsistence` Branch 4 @ line 955:
  'e->isOnBoundary()' — when the edge being processed has only one incident
  triangle (the other side is NULL / missing), Branch 4 clears the isclosed
  flag, indicating the mesh has open boundaries (holes).

The propagator walks edges of each triangle. When an edge's opposite triangle
pointer is NULL (boundary edge), Branch 4 fires and marks the mesh as not
closed. This is distinct from the normal-inconsistency branches (1-3) because
it detects topology (missing adjacent triangle) rather than winding.

Input pattern: an open mesh — a triangle strip with boundary edges. At least
one edge is shared by exactly 1 triangle (boundary edge), meaning 'isOnBoundary()'
returns true and Branch 4 fires.

Geometry: an L-shaped open strip of 4 triangles with multiple boundary edges.
    v0=(0,0,0), v1=(1,0,0), v2=(0,1,0), v3=(1,1,0), v4=(2,0,0), v5=(2,1,0)

    t0=(v0,v1,v3), t1=(v0,v3,v2)  — left square (consistent winding)
    t2=(v1,v4,v5), t3=(v1,v5,v3)  — right square (consistent winding)

    Interior edge shared by 2 triangles: (v0,v3), (v1,v3)
    All other edges are boundary (shared by exactly 1 triangle).

The mesh is open: boundary edges (v0,v1), (v0,v2), (v2,v3), (v3,v5), (v4,v5),
(v1,v4) each have only 1 incident triangle. forceNormalConsistence detects these
as isOnBoundary() → Branch 4: clear isclosed, return mesh-has-holes signal.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me433",
             title="forceNormalConsistence boundary-edge-detected: open mesh with boundary edges → isOnBoundary() clears isclosed (Branch 4)",
             defect_class="hole_in_hull")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2
v3 = m.vertex(1.0, 1.0, 0.0)   # 3
v4 = m.vertex(2.0, 0.0, 0.0)   # 4
v5 = m.vertex(2.0, 1.0, 0.0)   # 5

# Left square: CCW winding → normal +z.
t0 = m.triangle(v0, v1, v3)   # 0 — left lower
t1 = m.triangle(v0, v3, v2)   # 1 — left upper

# Right square: CCW winding → normal +z (consistently oriented).
t2 = m.triangle(v1, v4, v5)   # 2 — right lower
t3 = m.triangle(v1, v5, v3)   # 3 — right upper

# Interior edges (shared by 2 triangles).
# t0=(v0,v1,v3): edges (v0,v1),(v1,v3),(v0,v3). t1=(v0,v3,v2): (v0,v3),(v2,v3),(v0,v2).
# t2=(v1,v4,v5): (v1,v4),(v4,v5),(v1,v5). t3=(v1,v5,v3): (v1,v5),(v3,v5),(v1,v3).
# Interior: (v0,v3) in t0+t1; (v1,v3) in t0+t3; (v1,v5) in t2+t3.
m.assert_edge_shared(v0, v3, 2)   # t0 ↔ t1
m.assert_edge_shared(v1, v3, 2)   # t0 ↔ t3 — connection between left and right patches
m.assert_edge_shared(v1, v5, 2)   # t2 ↔ t3

# Boundary edges — each on exactly 1 triangle. isOnBoundary() → Branch 4.
m.assert_edge_shared(v0, v1, 1)   # t0 outer
m.assert_edge_shared(v0, v2, 1)   # t1 outer
m.assert_edge_shared(v2, v3, 1)   # t1 outer
m.assert_edge_shared(v1, v4, 1)   # t2 outer
m.assert_edge_shared(v4, v5, 1)   # t2 outer
m.assert_edge_shared(v3, v5, 1)   # t3 outer

# Hole boundary: the outer boundary loop of the open mesh.
m.assert_hole_boundary([v0, v1, v4, v5, v3, v2])
