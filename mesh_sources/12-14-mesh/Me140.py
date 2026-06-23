"""Me140 — isInnerPoint_empty_mesh: mesh has no triangles, early-return fires.

MeshFix `Basic_TMesh.isInnerPoint` Branch 1 (*empty_mesh*) @ line 1975:
  'if (!T.numels()) return false'
  The very first check in isInnerPoint tests whether the triangle list is
  empty. If there are no triangles the mesh cannot enclose any point, so
  the predicate returns false immediately.

Geometric signature: the fixture contains one isolated vertex with no
triangles referencing it. This is the minimal mesh that exercises the
empty-triangle-list early-return path. Any query point would immediately
return false.

Geometry:
  v0=(0,0,0)  — single isolated vertex
  (no triangles)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me140",
             title="isInnerPoint_empty_mesh: no triangles → T.numels()==0, early return false",
             defect_class="isolated_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — lone vertex, no triangles

# The single vertex is isolated (not referenced by any triangle).
m.assert_isolated_vertex(v0)
