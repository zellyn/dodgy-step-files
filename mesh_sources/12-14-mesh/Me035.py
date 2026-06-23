"""Me035 — border_face_removal: degenerate face on boundary removed without flip (Branch 13).

Catalog claim: a degenerate (zero-area) triangle lies on the mesh boundary
with one or more open (boundary) edges. The opposite face across its longest
edge is a null face (GT::null_face()) — so no flip is possible. CGAL
PMP.remove_degenerate_faces removes the face directly via remove_face
rather than attempting a flip.

Source: CGAL PMP.remove_degenerate_faces Branch 13 @ line 2292 —
*border-face-removal*: opposite_face == GT::null_face() (boundary edge);
face removed directly without flip operation.

Defect carrier: a manifold strip of 3 non-degenerate triangles forming an
open boundary mesh. A degenerate collinear triangle (t3) is appended at the
open boundary of the strip — its longest edge is a boundary edge (incident
on 1 face). The algorithm cannot flip across a null opposite face and instead
removes the face directly.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me035",
             title="border face removal: degenerate triangle on open boundary — direct remove_face",
             defect_class="degenerate_triangle")

# Three clean non-degenerate triangles forming an open strip (open mesh).
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(1.5, 1.0, 0.0)   # 3
v4 = m.vertex(2.0, 0.0, 0.0)   # 4

t0 = m.triangle(v0, v1, v2)   # face 0: clean
t1 = m.triangle(v1, v3, v2)   # face 1: clean
t2 = m.triangle(v1, v4, v3)   # face 2: clean

# Degenerate collinear triangle appended at the open boundary edge (v4, v3).
# v5 is on the line between v3 and v4 (collinear) — creates a zero-area face
# on the open boundary where the opposite face is null.
v5 = m.vertex(1.75, 0.5, 0.0)  # 5 — between v3=(1.5,1.0) and v4=(2.0,0.0)? No:
# Make it truly collinear: put v5 on the segment from v3 to v4.
# v3=(1.5,1.0,0), v4=(2.0,0.0,0), midpoint=(1.75,0.5,0) — that IS collinear.
# triangle(v3, v5, v4): v3,v5,v4 all on the segment → area=0, open boundary edge.
t3 = m.triangle(v3, v5, v4)   # face 3: DEGENERATE — v3, v5, v4 collinear; boundary

# Assert the degenerate triangle has zero area.
m.assert_triangle_area_lt(t3, 1e-12)

# Assert the boundary edges of the degenerate triangle (each shared by 1 face).
# Edge (v3, v4) connects to clean face t2 already, so it's shared by t2 AND t3 = 2.
# Actually v3,v4 is NOT an edge of t2. t2=(v1,v4,v3): edges are (v1,v4),(v4,v3),(v3,v1).
# So edge (v3,v4) is in t2 and t3 → shared by 2.
m.assert_edge_shared(v3, v4, 2)

# The edges (v3,v5) and (v5,v4) are new boundary edges shared by only t3.
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v5, v4, 1)
