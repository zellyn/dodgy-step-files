"""Me1122 — smoothing applied only to SI-bearing CC (smoothing-local-vs-global-focus branch).

CGAL PMP.remove_self_intersections Branch 8 @ line 2192 — *smoothing-local-vs-global-focus*:
  'if (self_intersects) { do_smooth = true; } else { do_smooth = treat_all_CCs; }'
  — the dispatcher conditions whether to apply smoothing on whether the current CC has
  an internal self-intersection. If use_smoothing is enabled and the CC has internal SI,
  smoothing fires; if the CC is SI-free and treat_all_CCs=false, smoothing is skipped.

Defect pattern: two connected components. CC-A (tris 0,1,2) has a self-intersecting
  triangle (tri 2, the intruder) crossing tri 0 — smoothing should fire locally on CC-A
  to relax the displaced vertex. CC-B (tris 3,4) is an SI-free flat patch 25 units away;
  when treat_all_CCs=false, smoothing is skipped for CC-B because self_intersects=false
  for that CC.

  CC-A geometry:
    - Flat base tri 0 = (v0,v1,v2) in z=0 (unit triangle).
    - Clean context tri 1 = (v1,v3,v2) adjacent to tri 0 (expands selection).
    - Intruder tri 2 = (v4,v5,v6): v4 at z=-0.5 pokes below patch, v5/v6 above.
  CC-B geometry (clean, 25 units away):
    - Tris 3,4 form a flat quad at y=25.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1122",
             title="local smoothing on SI-bearing CC only: treat_all_CCs=false skips clean CC-B",
             defect_class="self_intersection_smoothing_local")

# CC-A: base patch + intruder.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(1.5, 1.0, 0.0)   # 3

t0 = m.triangle(v0, v1, v2)    # tri 0 — CC-A base, z=0
t1 = m.triangle(v1, v3, v2)    # tri 1 — CC-A context, adjacent to tri 0

# Intruder in CC-A: no shared vertices → separate sub-CC. However, it is spatially
# within the SI region for CC-A's bounding box; it self-intersects tri 0.
v4 = m.vertex(0.5, 0.5, -0.5)  # 4 — below z=0 (displaced apex of intruder)
v5 = m.vertex(0.2, 0.5,  0.6)  # 5 — above z=0
v6 = m.vertex(0.8, 0.5,  0.6)  # 6 — above z=0
t2 = m.triangle(v4, v5, v6)    # tri 2 — CC-A intruder, crosses tri 0

# CC-B: clean flat quad 25 units away (no SI).
v7 = m.vertex(0.0, 25.0, 0.0)  # 7
v8 = m.vertex(1.0, 25.0, 0.0)  # 8
v9 = m.vertex(1.0, 26.0, 0.0)  # 9
v10 = m.vertex(0.0, 26.0, 0.0) # 10
t3 = m.triangle(v7, v8, v9)    # tri 3 — CC-B, clean
t4 = m.triangle(v7, v9, v10)   # tri 4 — CC-B, clean

# Assert: intruder self-intersects CC-A base.
m.assert_triangles_self_intersect(0, 2)

# Assert: CC-A context edge is interior (n=2).
m.assert_edge_shared(v1, v2, 2)

# Assert: CC-B is disconnected from CC-A.
m.assert_triangle_not_reachable_from(3, 0)

# Assert: CC-B interior edge is manifold.
m.assert_edge_shared(v7, v9, 2)
