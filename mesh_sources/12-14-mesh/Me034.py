"""Me034 — flip_impossible_degenerate: edge flip blocked by pre-existing edge (Branch 12).

Catalog claim: a degenerate (zero-area) triangle 2 sits adjacent to a pair
of triangles whose diagonal already exists — the candidate flip edge would
duplicate a pre-existing edge. CGAL PMP.remove_degenerate_faces detects
that 'flip is not possible' and removes the face directly instead, setting
all_removed=false.

Source: CGAL PMP.remove_degenerate_faces Branch 12 @ line 2256 —
*edge-flip-impossible*: the candidate flip would create an edge that already
exists in the mesh; face removal is used as fallback.

Defect carrier: four vertices in a diamond arrangement (v0-v3). Two clean
non-degenerate triangles (t0, t1) form a quad and share the diagonal (v1,v3).
A third degenerate collinear triangle (t2) also references v1 and v3 —
meaning the diagonal edge (v1,v3) is already shared by t0, t1, and t2
(3-way shared). Any attempt to flip t2's longest edge (v0-v3 or v1-v3)
collides with the pre-existing diagonal, making the flip impossible.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me034",
             title="flip-impossible degenerate: edge (v1,v3) already shared 3-way — face removal fallback",
             defect_class="degenerate_triangle")

# Diamond: v0 at top, v2 at bottom, v1 left, v3 right.
v0 = m.vertex(0.5, 1.0, 0.0)   # 0 — top
v1 = m.vertex(0.0, 0.0, 0.0)   # 1 — left
v2 = m.vertex(0.5,-1.0, 0.0)   # 2 — bottom
v3 = m.vertex(1.0, 0.0, 0.0)   # 3 — right

# Two clean non-degenerate triangles forming the diamond quad.
t0 = m.triangle(v0, v1, v3)   # face 0: upper-left, uses diagonal (v1, v3)
t1 = m.triangle(v2, v3, v1)   # face 1: lower, uses diagonal (v1, v3)

# Degenerate collinear triangle also referencing the v1-v3 diagonal.
# v4 is a collinear point between v1 and v3 on the x axis.
v4 = m.vertex(0.5, 0.0, 0.0)   # 4 — midpoint of v1..v3, collinear
t2 = m.triangle(v1, v4, v3)   # face 2: DEGENERATE — v1, v4, v3 are collinear (y=0)

# Assert degenerate triangle has zero area.
m.assert_triangle_area_lt(t2, 1e-12)

# Assert the diagonal (v1, v3) is shared 3-way — flip is impossible.
m.assert_edge_shared(v1, v3, 3)
