"""Me1113 — multiple SI types: one interior-disjoint pair filterable by filter NP.

Tests precondition that NP filter (filter_output_iterator / filter_t) would act on:
a mesh with two distinct self-intersecting pairs — one pair is "interior-disjoint"
(bounding boxes touch only at boundary, not in interior) and could be excluded by
a filter predicate; the other pair is a full interior crossing that must be processed.

Source: CGAL PMP.remove_self_intersections Branch 4 @ line 2413 —
*output-filter-applicability*: filter NP supplies a predicate to exclude certain
self-intersections from the repair queue (e.g. pairs whose intersection is
interior-disjoint). Branch fires when filter is non-null.

Geometry:
  Pair 1 (triangles 0,1): two triangles that cross through each other's interiors —
  a full geometric self-intersection. t0 lies in Z=0; t1 is tilted and cuts through.
  Pair 2 (triangles 2,3): two triangles that share only a single boundary point —
  they touch at exactly one corner of each triangle (vertex-touch only, no interior
  overlap). This "corner-touch" SI would be the candidate for filter exclusion.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1113",
    title="two SI pairs: interior crossing (must process) + corner-touch (filterable by filter NP)",
    defect_class="self_intersection_multi_type",
)

# Pair 1: full interior crossing (t0 in Z=0, t1 tilted through it).
p0 = m.vertex(0.0,  0.0,  0.0)  # 0
p1 = m.vertex(2.0,  0.0,  0.0)  # 1
p2 = m.vertex(1.0,  2.0,  0.0)  # 2
p3 = m.vertex(1.0, -1.0,  1.0)  # 3 — above Z=0
p4 = m.vertex(1.0,  1.0, -1.0)  # 4 — below Z=0
m.triangle(p0, p1, p2)    # tri 0 — Z=0 base triangle
m.triangle(p0, p3, p4)    # tri 1 — tilted through Z=0; intersects tri 0

# Pair 2: corner-touch only (shared single vertex at (5,0,0)).
# t2 and t3 each have one vertex at exactly the same 3D point — they "touch"
# at that corner but their interiors are disjoint (no interior overlap).
q_shared = m.vertex(5.0, 0.0, 0.0)  # 5 — shared corner (the "touch" point)
q0 = m.vertex(6.0, 1.0, 0.0)        # 6
q1 = m.vertex(6.0, -1.0, 0.0)       # 7
q2 = m.vertex(4.0, 1.0, 0.0)        # 8
q3 = m.vertex(4.0, -1.0, 0.0)       # 9
m.triangle(q_shared, q0, q1)  # tri 2 — right of shared corner
m.triangle(q_shared, q2, q3)  # tri 3 — left of shared corner; touches tri 2 at corner

# Assert: Pair 1 is a full interior crossing.
m.assert_triangles_self_intersect(0, 1)

# Assert: Pair 2 shares no triangle interior — triangles are disconnected components.
m.assert_triangle_not_reachable_from(2, 0)
