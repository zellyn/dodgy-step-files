"""Me340 — init_info_array_allocation_triangles: t_info array sized to triangle count at init.

MeshFix `Basic_TMesh.init` Branch 1 (*INFO_ARRAY_ALLOCATION_TRIANGLES*) @ line 190:
  't_info = new void *[tin->T.numels()]' — allocates a pointer array exactly as large as
  the number of triangles in the source mesh. If the triangle count is wrong (e.g. duplicate
  triangles inflate the count) the allocated buffer is over-sized relative to the actual
  unique triangle topology.

Defect pattern: a 4-triangle mesh where two triangles are exact duplicates (same vertex set).
  The init call will size t_info to 4, but only 3 unique face connections exist. This
  demonstrates the defect class that Branch 1 is sensitive to: an inflated triangle count
  causes t_info to be larger than the real topology needs.

Geometry: quad (v0,v1,v2,v3) split into 2 valid triangles + 1 duplicate triangle + 1 control.
  t0=(v0,v1,v2), t1=(v0,v2,v3) — valid quad split.
  t2=(v0,v1,v2) — exact duplicate of t0 (causes inflated triangle count).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me340",
             title="init_info_array_allocation_triangles: duplicate triangle inflates t_info allocation size",
             defect_class="duplicate_triangles")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)

t0 = m.triangle(v0, v1, v2)   # 0: upper-right triangle
t1 = m.triangle(v0, v2, v3)   # 1: upper-left triangle
t2 = m.triangle(v0, v1, v2)   # 2: duplicate of t0 — inflates T.numels()

# Confirm the duplicate pair (t0 and t2 share the same vertex set).
m.assert_duplicate_triangle_pair(0, 2)

# Shared diagonal edge — appears on 3 triangles due to duplicate.
m.assert_edge_shared(v0, v2, 3)

# Control: the other diagonal is not duplicated.
m.assert_edge_shared(v0, v1, 2)
