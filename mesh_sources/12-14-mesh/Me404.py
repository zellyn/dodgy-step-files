"""Me404 — detect_identical_mergeable_vertices group_break: target point differs after a group; inner while exits (Branch 5).

CGAL PMP `PMP.internal.detect_identical_mergeable_vertices` Branch 5 (*group_break*) @ line 182:
  'else { ++i; break; }'
  — inside the inner while loop collecting consecutive halfedges with identical target,
  the loop exits when the current halfedge's target point differs from the previous.
  The 'else' branch increments i once more and breaks out, terminating the group.

Defect pattern: four triangles with a hexagonal boundary cycle containing exactly one
  pair of coincident boundary vertices (b1 and b3 at (1,0,0)), surrounded on both sides
  by non-coincident boundary vertices. After sorting, the boundary halfedge sequence is:
  [... target=b0(distinct) ... target=b1(1,0,0) ... target=b3(1,0,0) ... target=b4(distinct) ...]
  The inner while collects b1 and b3 into a group, then encounters b4 (different
  coordinate) → Branch 5 fires (else branch, ++i, break).

Geometry:
  b0=(0,0,0), b1=(1,0,0) [coincident with b3], b2=(2,1,0), b3=(1,0,0), b4=(0,2,0)
  Four triangles: hub at b5=(1,1,0) with fan.

  Design: fan from b5 with boundary vertices b0,b1,b2,b3,b4.
  b1 and b3 coincident; none share the same triangle.
  t0=(b5,b0,b1): left-bottom. Boundary: (b0,b1),(b0,b5),(b1,b5)[shared?].
  Need shared interior edges to form single boundary cycle.

  Clean layout:
    b5=(1,1,0) hub.
    t0=(b5,b0,b1), t1=(b5,b1,b2) [shares (b5,b1) → interior]... but b1 in both!
    (b5,b1) n=2 if in t0 and t1. Then b1 is NOT a boundary vertex — it's interior.
    Need b1 to be on the boundary.

  For b1 to be a boundary vertex, no two triangles may share an edge containing b1.
  Use b1 in exactly ONE triangle.

  Four-triangle strip with separate left and right sectors:
    b0=(0,0,0), b1=(1,0,0)[coinc, in t0 only], b2=(2,0,0),
    b3=(1,0,0)[coinc with b1, in t2 only], b4=(2,2,0), b5=(0,2,0)
    t0=(b0,b1,b5): b1 in boundary at (1,0,0).
    t1=(b0,b2,b5)? shares (b0,b5)? w/ t0? Only if t0 uses (b0,b5).
    t0 edges: (b0,b1),(b1,b5),(b0,b5).
    t1=(b2,b4,b5): t1 edges: (b2,b4),(b4,b5),(b2,b5). No sharing with t0.
    t2=(b2,b3,b4): b3 in boundary. t2 edges: (b2,b3),(b3,b4),(b2,b4).
    Sharing (b2,b4) between t1 and t2 → interior.
    t3=(b0,b2,b5): connects the two clusters. t3 edges: (b0,b2),(b2,b5),(b0,b5).
    Sharing: (b0,b5) in t0 and t3 → interior. (b2,b5) in t1 and t3 → interior.
    All interior: (b0,b5),(b2,b4),(b2,b5).
    Boundary: (b0,b1),(b1,b5),(b4,b5),(b3,b4),(b2,b3),(b0,b2).
    Wait (b0,b2) only in t3? Yes → boundary.
    Cycle: b0→b1→b5→b4→b3→b2→b0 (or some ordering).
    b1 and b3 both at (1,0,0) — surrounded by b0,b5 and b4,b2 respectively.
    No triangle contains both b1 and b3.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me404",
    title="detect_identical_mergeable_vertices group_break: coincident b1==b3 at (1,0,0) bounded by distinct neighbors; inner while exits via else branch (Branch 5)",
    defect_class="near_coincident_vertex",
)

b0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left base (distinct)
b1 = m.vertex(1.0, 0.0, 0.0)  # 1 — boundary at (1,0,0); coincident with b3
b2 = m.vertex(2.0, 0.0, 0.0)  # 2 — right base (distinct)
b3 = m.vertex(1.0, 0.0, 0.0)  # 3 — boundary at (1,0,0); coincident with b1
b4 = m.vertex(2.0, 2.0, 0.0)  # 4 — upper right (distinct)
b5 = m.vertex(0.0, 2.0, 0.0)  # 5 — upper left (distinct)

# Four triangles: two left-sector, two right-sector, connected by shared interior edges.
t0 = m.triangle(b0, b1, b5)  # 0: left-bottom [b1 on boundary]
t1 = m.triangle(b2, b4, b5)  # 1: right-top
t2 = m.triangle(b2, b3, b4)  # 2: right-bottom [b3 on boundary]
t3 = m.triangle(b0, b2, b5)  # 3: connector

# Interior shared edges (n=2).
m.assert_edge_shared(b0, b5, 2)  # t0 and t3
m.assert_edge_shared(b2, b4, 2)  # t1 and t2
m.assert_edge_shared(b2, b5, 2)  # t1 and t3

# Boundary edges (n=1).
m.assert_edge_shared(b0, b1, 1)  # t0 bottom-left
m.assert_edge_shared(b1, b5, 1)  # t0 left side
m.assert_edge_shared(b4, b5, 1)  # t1 top
m.assert_edge_shared(b3, b4, 1)  # t2 right
m.assert_edge_shared(b2, b3, 1)  # t2 bottom-right
m.assert_edge_shared(b0, b2, 1)  # t3 bottom

# Coincident pair b1, b3 — each in a different triangle, no shared triangle.
# In boundary cycle, b1 and b3 are bounded by distinct-coordinate neighbors
# (b0 and b5 flank b1; b2 and b4 flank b3).
# After the group {b1,b3} is collected, the next halfedge target differs → Branch 5.
m.assert_vertex_pair_distance_lt(b1, b3, 1e-9)
m.assert_vertex_pair_no_shared_triangle(b1, b3)

# Euler: V=6, E=9, F=4, chi=1 (open disk).
m.assert_euler_characteristic(6, 9, 4, 1)
