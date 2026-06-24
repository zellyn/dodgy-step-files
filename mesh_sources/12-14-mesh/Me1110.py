"""Me1110 — non-manifold pinch-neck vertex with crossing fan: genus-preservation branch.

Tests precondition that NP preserve_genus would act on: a non-manifold (bowtie)
vertex whose disconnected fan signals that duplicating the shared vertex is needed
before SI removal when preserve_genus=false.

Source: CGAL PMP.remove_self_intersections Branch 1 @ line 2379 —
*genus-preservation-requirement*: preserve_genus NP controls whether non-manifold
vertices are duplicated before hole-filling. Branch fires when the mesh has a
non-manifold vertex and preserve_genus is being evaluated.

Geometry: vertex 0 is a pinch-neck shared by two disconnected triangle fans.
Fan A (triangles 0,1): two coplanar triangles in the Z=0 plane, left of hub.
Fan B (triangles 2,3): two triangles in the Y=0 plane, one of which (tri 3)
crosses the Z=0 plane and self-intersects with triangle 0 from fan A.
The hub vertex fan is disconnected — typical non-manifold bowtie pattern.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1110",
    title="pinch-neck non-manifold vertex: genus-preservation decision for SI removal",
    defect_class="self_intersection_non_manifold_vertex",
)

# Pinch-neck hub at origin.
hub = m.vertex(0.0, 0.0, 0.0)   # 0 — bowtie / pinch-neck hub

# Fan A: two triangles in Z=0 plane; no edge shared with fan B.
fa0 = m.vertex(-1.0,  1.0, 0.0)  # 1
fa1 = m.vertex(-2.0,  0.0, 0.0)  # 2
fa2 = m.vertex(-1.0, -1.0, 0.0)  # 3
m.triangle(hub, fa0, fa1)   # tri 0 — fan A, upper left
m.triangle(hub, fa1, fa2)   # tri 1 — fan A, lower left

# Fan B: two triangles in Y=0 plane.
# tri 2 stays in Y=0; tri 3 dips below Z=0 and crosses tri 0's plane.
fb0 = m.vertex(1.0, 0.0,  1.0)  # 4
fb1 = m.vertex(2.0, 0.0,  0.0)  # 5
fb2 = m.vertex(1.0, 0.0, -1.0)  # 6
fb3 = m.vertex(-0.5, 0.0, -0.5) # 7 — apex crossing into Z<0 territory of fan A
m.triangle(hub, fb0, fb1)   # tri 2 — fan B, right side (Y=0)
m.triangle(hub, fb2, fb3)   # tri 3 — fan B, crosses Z=0 plane; intersects tri 0

# Assert: hub has disconnected vertex fan (non-manifold / bowtie).
m.assert_vertex_fan_disconnected(hub)

# Assert: tri 0 (Z=0) and tri 3 (crosses Z=0) self-intersect.
m.assert_triangles_self_intersect(0, 3)
