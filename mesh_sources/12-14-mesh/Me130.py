"""Me130 — removeIfRedundant_not_double_flat: vertex has a 3D (non-flat) fan.

MeshFix `Vertex.removeIfRedundant` Branch 1 (*not_double_flat*) @ line 346:
  'if (!isDoubleFlat && !isFlat(...))'
  If the vertex is neither DoubleFlat nor Flat, removeIfRedundant immediately
  returns false — the vertex is non-redundant because its removal would change
  the shape of the surface.

Geometric signature: vertex v4 sits at the apex of a pyramid. Its four incident
triangles form a non-planar fan (the apex is above the z=0 base). The vertex
cannot be collapsed without altering the geometry; removeIfRedundant must return
false at the first branch.

Geometry:
  Base square: v0=(0,0,0), v1=(1,0,0), v2=(1,1,0), v3=(0,1,0)
  Apex: v4=(0.5, 0.5, 1.0)   ← 3D, non-flat → triggers Branch 1 rejection

  Four pyramid faces:
    t0 = (v0, v1, v4)
    t1 = (v1, v2, v4)
    t2 = (v2, v3, v4)
    t3 = (v3, v0, v4)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me130",
             title="removeIfRedundant_not_double_flat: apex vertex has non-planar 3D fan, removal blocked",
             defect_class="redundant_vertex_removal_blocked")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — base corner
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — base corner
v2 = m.vertex(1.0, 1.0, 0.0)   # 2 — base corner
v3 = m.vertex(0.0, 1.0, 0.0)   # 3 — base corner
v4 = m.vertex(0.5, 0.5, 1.0)   # 4 — pyramid apex: non-flat, 3D

t0 = m.triangle(v0, v1, v4)    # 0
t1 = m.triangle(v1, v2, v4)    # 1
t2 = m.triangle(v2, v3, v4)    # 2
t3 = m.triangle(v3, v0, v4)    # 3

# All four apex edges are interior (shared by exactly 2 triangles): confirms
# the closed fan around v4.
m.assert_edge_shared(v0, v4, 2)   # shared by t0 and t3
m.assert_edge_shared(v1, v4, 2)   # shared by t0 and t1
m.assert_edge_shared(v2, v4, 2)   # shared by t1 and t2
m.assert_edge_shared(v3, v4, 2)   # shared by t2 and t3
