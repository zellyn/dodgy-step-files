"""Me314 — watsonInsert_no_circumsphere_triangles: empty cavity — point outside triangulation.

MeshFix `holeFilling::watsonInsert` Branch 5 (*NO_CIRCUMSPHERE_TRIANGLES*) @ line 320:
  'if (bdr.numels() == 0) return NULL'
  After the Bowyer-Watson cavity walk, if no triangles contained the point in
  their circumsphere the boundary list 'bdr' is empty. The function returns
  NULL immediately — the point is outside the triangulation and cannot be
  inserted. This is the "point outside triangulation" failure path.

Defect pattern: two completely separate triangle patches with a gap between
  them. The inserted point lies in the gap (outside both patches). No
  triangle's circumsphere contains the point — bdr is empty — Branch 5 fires.

Geometry: two separate triangles in the z=0 plane, separated by a gap.
  Patch A: v0=(0,0,0), v1=(1,0,0), v2=(0,1,0) — lower-left triangle.
  Patch B: v3=(3,0,0), v4=(4,0,0), v5=(3,1,0) — upper-right triangle.

  The gap between them means a point at (2,0.5,0) is outside all circumspheres.
  In terms of our JSON model: two disjoint triangles are the 'pre-insertion'
  state; the failure of insertion is represented by the gap (no edge connects
  the two patches).

We assert the disconnected topology: t1 is not reachable from t0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me314",
             title="watsonInsert_no_circumsphere_triangles: point outside all circumspheres returns NULL (Branch 5)",
             defect_class="hole_in_hull")

# Patch A — lower-left.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2

# Patch B — upper-right (separated by gap: x=2 is the midpoint in the void).
v3 = m.vertex(3.0, 0.0, 0.0)   # 3
v4 = m.vertex(4.0, 0.0, 0.0)   # 4
v5 = m.vertex(3.0, 1.0, 0.0)   # 5

t0 = m.triangle(v0, v1, v2)   # 0 — Patch A
t1 = m.triangle(v3, v4, v5)   # 1 — Patch B (disconnected)

# All edges are boundary (incident on exactly 1 triangle).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)

# The two triangles are in different connected components — no shared edge.
m.assert_triangle_not_reachable_from(target=1, source=0)
