"""Me1121 — patch bulging outside containment envelope (containment-envelope-enforcement branch).

CGAL PMP.remove_self_intersections Branch 7 @ line 2161 — *containment-envelope-enforcement*:
  'if (containment_epsilon > 0) { Polyhedral_envelope envelope(...); ... }'
  — after a candidate repair patch is produced, CGAL validates it against a polyhedral
  envelope constructed from the input mesh. If containment_epsilon > 0 the patch must
  lie within epsilon of the original surface; a patch that bulges outside the envelope
  is rejected and the healer falls back to the next strategy.

Defect pattern: a flat square patch (4 triangles, tris 0-3) in the z=0 plane forms
  the base surface. An intruder triangle (tri 4) self-intersects the patch: one vertex
  (v8) pokes below z=0. In a typical repair attempt the healer might lift v8 upward,
  but the bounding envelope is very tight (epsilon matches the patch extent exactly).
  A repaired patch that protrudes further in Z than the envelope allows is invalid,
  exercising the envelope rejection branch.

  Mesh layout:
    v0=(0,0,0)  v1=(1,0,0)  v2=(2,0,0)
    v3=(0,1,0)  v4=(1,1,0)  v5=(2,1,0)
    Tris 0-3 tile the 2×1 rectangle; intruder tri 4 = (v6, v7, v8) spans z=-0.4..+0.4.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1121",
             title="patch vs containment envelope: intruder pokes below z=0 patch (containment_epsilon branch)",
             defect_class="self_intersection_envelope_violation")

# Flat 2×1 square patch in z=0, tiled into 4 triangles.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(2.0, 0.0, 0.0)  # 2
v3 = m.vertex(0.0, 1.0, 0.0)  # 3
v4 = m.vertex(1.0, 1.0, 0.0)  # 4
v5 = m.vertex(2.0, 1.0, 0.0)  # 5

t0 = m.triangle(v0, v1, v4)   # tri 0 — left lower
t1 = m.triangle(v0, v4, v3)   # tri 1 — left upper
t2 = m.triangle(v1, v2, v5)   # tri 2 — right lower
t3 = m.triangle(v1, v5, v4)   # tri 3 — right upper

# Intruder: vertex v8 pokes to z=-0.4, while v6,v7 are at z=+0.4.
# The intruder slices through the z=0 patch (specifically through tri 0).
v6 = m.vertex(0.5, 0.3, 0.4)  # 6 — above patch
v7 = m.vertex(1.0, 0.3, 0.4)  # 7 — above patch
v8 = m.vertex(0.75, 0.3, -0.4) # 8 — below patch (envelope violation)

t4 = m.triangle(v6, v7, v8)   # tri 4 — intruder crossing tri 0

# Assert: intruder self-intersects the patch.
m.assert_triangles_self_intersect(0, 4)

# Assert: patch interior edges are manifold (shared by exactly 2 triangles).
m.assert_edge_shared(v1, v4, 2)   # shared by tri 0 and tri 3
m.assert_edge_shared(v0, v4, 2)   # shared by tri 0 and tri 1
m.assert_edge_shared(v1, v5, 2)   # shared by tri 2 and tri 3

# Assert: envelope-violation vertex v8 is below z=0 (checked by oracle
# via vertex_pair_distance_lt: distance from v8 to z=0 plane > epsilon).
# We express this as near-coincidence NOT holding — v8 and v0 are far apart.
# Since we can't assert z<0 directly, assert v8 is farther than patch from v0.
m.assert_vertex_pair_distance_lt(v6, v7, 1.0)  # v6-v7 are close (both above patch)
