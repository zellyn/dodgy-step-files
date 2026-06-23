"""Me016 — SI + non-manifold bowtie vertex (genus-preservation branch).

Catalog claim: vertex 0 is a bowtie hub shared by two disconnected triangle fans.
Fans A (triangles 0,1) and B (triangles 2,3) share only the hub. Triangles 0 and
3 are coplanar in z=0 with overlapping interiors — a coplanar self-intersection.
The self-intersection removal path must decide whether to preserve topological genus
by duplicating the non-manifold vertex before hole-filling.

Source: CGAL PMP.remove_self_intersections Branch 1 @ line 2379 —
*genus-preservation-requirement*: whether to preserve topological genus
(preserve_genus NP) by duplicating non-manifold vertices.

Defect carrier: bowtie hub at origin. Fan A = triangles 0 and 1 (both in z=0
plane, separated). Fan B = triangles 2 and 3 (triangle 3 coplanar with fan A,
overlapping tri 0's interior). Fan A and fan B share only the hub vertex, giving
a disconnected vertex fan. Tri 0 and tri 3 overlap in 2D projection.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me016",
             title="SI + non-manifold bowtie vertex: genus-preservation decision",
             defect_class="self_intersection_non_manifold_vertex")

hub = m.vertex(0.0, 0.0, 0.0)    # 0 — bowtie hub

# Fan A (z=0 plane): two triangles sharing only hub.
a0 = m.vertex(2.0,  0.0, 0.0)    # 1
a1 = m.vertex(2.0,  1.0, 0.0)    # 2
a2 = m.vertex(-2.0, 0.0, 0.0)    # 3
a3 = m.vertex(-2.0, 1.0, 0.0)    # 4
m.triangle(hub, a0, a1)   # tri 0 — fan A right (z=0)
m.triangle(hub, a2, a3)   # tri 1 — fan A left  (z=0)

# Fan B: two triangles sharing only hub. Triangle 3 is coplanar with fan A
# and overlaps tri 0's interior.
b0 = m.vertex(0.0,  0.5, -1.0)   # 5
b1 = m.vertex(0.0,  0.5,  1.0)   # 6
b2 = m.vertex(0.0, -1.0,  0.0)   # 7
b3 = m.vertex(1.5,  0.5,  0.0)   # 8 — extends into fan A right's XY territory
m.triangle(hub, b0, b1)   # tri 2 — fan B, spans z=-1..+1
m.triangle(hub, b2, b3)   # tri 3 — fan B, coplanar z=0, overlaps tri 0

# Assert: bowtie vertex fan is disconnected.
m.assert_vertex_fan_disconnected(hub)

# Assert: tri 0 and tri 3 self-intersect (coplanar area overlap).
m.assert_triangles_self_intersect(0, 3)
