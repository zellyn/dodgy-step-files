"""Me862 — strongIntersectionRemoval selection-growth depth: growSelection ring expansion.

Catalog claim: the initial SI pair lies deep inside a surrounding belt of
triangles; the removal loop must expand the selected region multiple rings
outward (for n=1, then n=2, ...) via growSelection before the selection is
large enough to contain a repairable region. This exercises Branch 3 where
iter_count drives an increasing growth depth.

Source: MeshFix `Basic_TMesh.strongIntersectionRemoval` Branch 3 @ line 383 —
*Selection-growth depth*: for (n=1...) growSelection ring expansion — on each
repair pass the growth ring count n equals the current iteration number,
so the selected region expands further on stubborn configurations.

Defect carrier: triangle 0 (XY plane) and triangle 1 (intruder) form the
core SI pair. Triangles 2-5 form a first-ring belt sharing edges with
triangle 0. Triangles 6-9 form a second-ring belt sharing edges with the
first belt. The multi-ring surrounding belt means a single growSelection(1)
call does not fully encompass the repair context; growth must proceed to
ring 2 (n=2) before the selection is sufficient.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me862",
    title="strongIntersectionRemoval selection-growth depth: multi-ring growSelection expansion (Branch 3)",
    defect_class="self_intersection",
)

# Core: SI pair at the center.
# Triangle 0: flat base in XY plane.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2

# Triangle 1: intruder that crosses triangle 0 through its midpoint.
v3 = m.vertex(1.0, 0.7,  1.5)  # 3 — above z=0
v4 = m.vertex(1.0, 0.7, -1.5)  # 4 — below z=0 (defect: pierces tri 0)
v5 = m.vertex(2.5, 0.7,  0.0)  # 5 — in z=0 plane, outside tri 0

m.triangle(v0, v1, v2)   # tri 0 — core base (XY)
m.triangle(v3, v4, v5)   # tri 1 — core intruder (crosses tri 0)

# First ring: 4 triangles sharing edges with triangle 0.
# They extend outward from each edge of tri 0.
v6  = m.vertex(-1.0,  0.0, 0.0)  # 6
v7  = m.vertex( 3.0,  0.0, 0.0)  # 7
v8  = m.vertex( 1.0, -2.0, 0.0)  # 8
v9  = m.vertex(-0.5,  2.5, 0.0)  # 9
v10 = m.vertex( 2.5,  2.5, 0.0)  # 10

m.triangle(v0, v6, v1)    # tri 2 — ring1 below (shares v0-v1 with tri 0)
m.triangle(v1, v7, v2)    # tri 3 — ring1 right  (shares v1-v2 with tri 0)
m.triangle(v2, v9, v0)    # tri 4 — ring1 left   (shares v2-v0 with tri 0)
m.triangle(v0, v8, v1)    # tri 5 — ring1 front  (shares v0-v1 below)

# Second ring: 4 triangles extending further from the first ring.
v11 = m.vertex(-2.0,  0.0, 0.0)  # 11
v12 = m.vertex( 4.0,  0.0, 0.0)  # 12
v13 = m.vertex( 1.0, -4.0, 0.0)  # 13
v14 = m.vertex(-1.5,  4.0, 0.0)  # 14
v15 = m.vertex( 3.5,  4.0, 0.0)  # 15

m.triangle(v6,  v11, v1)   # tri 6 — ring2 bottom-left  (shares v6-v1 with tri 2)
m.triangle(v7,  v12, v2)   # tri 7 — ring2 right        (shares v7-v2 with tri 3)
m.triangle(v9,  v14, v0)   # tri 8 — ring2 upper-left   (shares v9-v0 with tri 4)
m.triangle(v8,  v13, v1)   # tri 9 — ring2 bottom-right (shares v8-v1 with tri 5)

# Assert: the core pair self-intersects (triggers growth-depth expansion).
m.assert_triangles_self_intersect(0, 1)

# Assert: first-ring triangles share edges with the core (confirm adjacency for ring growth).
m.assert_edge_shared(v0, v1, 3)  # tri 0, tri 2, tri 5 all share v0-v1

# Assert: second-ring triangles share edges with first ring (multi-ring structure).
m.assert_edge_shared(v6, v1, 2)   # tri 2 and tri 6 share v6-v1
m.assert_edge_shared(v7, v2, 2)   # tri 3 and tri 7 share v7-v2
