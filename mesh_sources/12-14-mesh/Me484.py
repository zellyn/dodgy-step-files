"""Me484 — removeTriangles triangle_removal: T.removeCell + delete t; orphan triangle unlinked.

Basic_TMesh.removeTriangles branch 5: triangle_removal —
  `T.removeCell(n); delete t;`

After detecting that a triangle has at least one NULL edge pointer (branches 2-4),
the algorithm removes it from the triangle list and frees its memory. The
geometric precondition is a mesh that has just had orphan-triangle cleanup run:
the resulting mesh contains only the surviving intact triangles.

Fixture: a 3-triangle fan around a central vertex. One triangle (t2) is
degenerate — its three vertices are collinear (zero area), so any edge-validity
filter would null one of its edge pointers and queue it for T.removeCell in
Branch 5. The two healthy triangles (t0, t1) represent the post-removal
survivor state.

Geometry (z = 0):
  v0=(0,0,0), v1=(2,0,0), v2=(1,0,0) — v2 lies exactly on segment v0-v1
  v3=(1,1,0)

  t0 = (v0, v3, v2)  — healthy, area=0.5
  t1 = (v1, v2, v3)  — healthy, area=0.5
  t2 = (v0, v1, v2)  — degenerate: collinear on y=0 → area=0
                        this is the triangle removed by T.removeCell (Branch 5)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me484",
             title="removeTriangles triangle_removal: T.removeCell+delete t; t2=[v0,v1,v2] is collinear orphan to be removed (Branch 5)",
             defect_class="degenerate_triangle")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 0.0, 0.0)   # 2 — midpoint on v0-v1
v3 = m.vertex(1.0, 1.0, 0.0)   # 3

t0 = m.triangle(v0, v3, v2)    # 0 — healthy, area=0.5
t1 = m.triangle(v1, v2, v3)    # 1 — healthy, area=0.5
t2 = m.triangle(v0, v1, v2)    # 2 — degenerate: v0, v1, v2 collinear on y=0

# t2 is the orphan triangle: area=0, would be removed by T.removeCell.
m.assert_triangle_area_lt(2, 1e-12)

# t0 and t1 are healthy survivors.
m.assert_triangle_area_lt(0, 1.0)   # area(t0)=0.5 < 1.0
m.assert_triangle_area_lt(1, 1.0)   # area(t1)=0.5 < 1.0

# v2 lies exactly on segment v0-v1 (midpoint).
m.assert_vertex_on_edge(v2, v0, v1)
