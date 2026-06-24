"""Me395 — do_faces_intersect branch 6: full-geometric-triangle-si.

PMP.do_faces_intersect Branch 6 (*full-geometric-triangle-si*) @ line 303:
  When two faces share NO vertex and NO edge, the function falls through to the
  full geometric triangle-triangle intersection test: `do_intersect(th, tg)`.
  Branch 6 fires when this pure geometric test returns true — the triangles cross
  without any topological adjacency.

The fixture models two triangles with completely disjoint vertex sets that cross
each other geometrically. t0 lies in the XY plane (z=0); t1 is near-vertical
with its edge (v3,v4) passing through t0's interior at point (1,1,0).

Geometry (no shared vertices):
  t0: v0=(0,0,0), v1=(3,0,0), v2=(0,3,0)  — XY-plane triangle
  t1: v3=(1,1,-2), v4=(1,1,2), v5=(5,5,0) — near-vertical; edge v3-v4 pierces t0
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me395",
    title="do_faces_intersect full-geometric-SI: no shared vertex or edge, triangles cross geometrically (Branch 6)",
    defect_class="self_intersection_face_pair",
)

# Triangle 0: in XY plane (z=0).
v0 = m.vertex(0.0, 0.0,  0.0)  # 0
v1 = m.vertex(3.0, 0.0,  0.0)  # 1
v2 = m.vertex(0.0, 3.0,  0.0)  # 2

# Triangle 1: near-vertical; edge (v3,v4) pierces t0 at (1,1,0). No shared vertices.
v3 = m.vertex(1.0, 1.0, -2.0)  # 3: below XY plane
v4 = m.vertex(1.0, 1.0,  2.0)  # 4: above XY plane
v5 = m.vertex(5.0, 5.0,  0.0)  # 5: far apex (not in t0's interior)

t0 = m.triangle(v0, v1, v2)   # 0: XY-plane triangle
t1 = m.triangle(v3, v4, v5)   # 1: near-vertical triangle piercing t0

# No shared vertices between t0 and t1.
m.assert_vertex_pair_no_shared_triangle(v0, v3)
m.assert_vertex_pair_no_shared_triangle(v1, v4)
# Pure geometric self-intersection — Branch 6 (do_intersect(th, tg)) path.
m.assert_triangles_self_intersect(t0, t1)
