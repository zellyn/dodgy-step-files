"""Me952 — Basic_TMesh.checkGeometry duplicate_vertex_with_edge: coincident vertices connected by zero-length edge (Branch 3).

MeshFix `Basic_TMesh.checkGeometry` Branch 3 (*duplicate_vertex_with_edge*) @ line 208:
  'getEdge(v2) != null' — two vertices at the same geometric point ARE connected by
  a half-edge (they appear in the same triangle). This is a severe defect: the edge
  has zero length, making it degenerate. checkGeometry returns the first coincident
  vertex (v1) as the error location immediately, without continuing the scan.

Defect pattern: a triangle where two vertices (v0 and v1) are at the same
coordinate. A half-edge from v0 to v1 therefore exists with length 0. When the
sorted vertex array sees v0 and v1 adjacent with distance 0, it calls
getEdge(v1) from v0 — this returns non-null because t1 references both v0 and
v1 → Branch 3 fires, returning v0 as the defect location.

Geometry: one clean control triangle plus one degenerate triangle.
  t0=(v3,v4,v5): clean triangle (added first for predictable indices).
  t1=(v0,v1,v2): v0=(1,0,0), v1=(1,0,0) [same coords], v2=(0,1,0).
    Edge (v0,v1) has length 0 → degenerate; triangle area = 0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me952",
    title="Basic_TMesh.checkGeometry duplicate_vertex_with_edge: v0==v1 at (1,0,0), zero-length edge (Branch 3)",
    defect_class="coincident_vertices",
)

# Triangle 0 (control) — clean triangle.
v3 = m.vertex(0.0, 0.0, 0.0)    # 0
v4 = m.vertex(2.0, 0.0, 0.0)    # 1
v5 = m.vertex(1.0, 1.0, 0.0)    # 2
m.triangle(v3, v4, v5)           # t0 — clean control

# Triangle 1 (defective): v0 and v1 at identical position (1,0,0).
v0 = m.vertex(1.0, 0.0, 0.0)    # 3 — coincident with v1
v1 = m.vertex(1.0, 0.0, 0.0)    # 4 — exact coincidence with v0
v2 = m.vertex(0.0, 1.0, 0.0)    # 5
m.triangle(v0, v1, v2)           # t1 — edge (v0,v1) has length 0

# v0 and v1 are exactly coincident (distance = 0).
m.assert_vertex_pair_distance_lt(v0, v1, 1e-12)
# Degenerate triangle has zero area (v0==v1 as coordinates → zero cross product).
m.assert_triangle_area_lt(1, 1e-12)
# Edge (v0,v1) exists as a boundary edge (shared by exactly 1 triangle).
m.assert_edge_shared(v0, v1, 1)
