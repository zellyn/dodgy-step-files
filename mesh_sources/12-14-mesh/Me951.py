"""Me951 — Basic_TMesh.checkGeometry duplicate_vertices: coincident vertices without connecting edge (Branch 2).

MeshFix `Basic_TMesh.checkGeometry` Branch 2 (*duplicate_vertices*) @ line 204:
  'xyzCompare' — after sorting all vertices by coordinate, consecutive entries
  that are spatially coincident are detected. If getEdge(v2) returns null (no
  half-edge connects the two coincident vertices), a warning is logged and the
  scan continues (Branch 2 fires). The function does NOT return early here —
  it records the defect and continues scanning.

Defect pattern: two vertices at the exact same position (0,0,0) that belong
to separate triangles with no shared edge or triangle. In the sorted vertex
array, these two entries are adjacent and have distance 0, triggering the
duplicate detection. Since no edge connects them, getEdge returns null →
Branch 2 fires.

Geometry: two isolated triangles.
  t0=(v0,v1,v2): v0=(0,0,0) [coincident with v3], v1=(1,0,0), v2=(0.5,1,0)
  t1=(v3,v4,v5): v3=(0,0,0) [coincident with v0], v4=(2,0,0), v5=(1.5,1,0)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me951",
    title="Basic_TMesh.checkGeometry duplicate_vertices: v0==v3 at (0,0,0) in separate triangles, no edge (Branch 2)",
    defect_class="coincident_vertices",
)

# Triangle 0: contains v0 at (0,0,0).
v0 = m.vertex(0.0, 0.0, 0.0)    # 0 — coincident with v3
v1 = m.vertex(1.0, 0.0, 0.0)    # 1
v2 = m.vertex(0.5, 1.0, 0.0)    # 2
m.triangle(v0, v1, v2)           # t0

# Triangle 1: contains v3 at (0,0,0) — exact coincidence with v0.
v3 = m.vertex(0.0, 0.0, 0.0)    # 3 — coincident with v0 (distance = 0)
v4 = m.vertex(2.0, 0.0, 0.0)    # 4
v5 = m.vertex(1.5, 1.0, 0.0)    # 5
m.triangle(v3, v4, v5)           # t1

# v0 and v3 are exactly coincident.
m.assert_vertex_pair_distance_lt(v0, v3, 1e-12)
# v0 and v3 share no triangle — getEdge returns null → Branch 2.
m.assert_vertex_pair_no_shared_triangle(v0, v3)
