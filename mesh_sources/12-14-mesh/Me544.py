"""Me544 — checkAndRepair::removeDegenerateTriangles branch 5: NEEDLE_EDGE_COINCIDENT_ENDPOINTS

MeshFix `checkAndRepair::removeDegenerateTriangles` Branch 5 (*NEEDLE_EDGE_COINCIDENT_ENDPOINTS*) @ line 504:
  'if ((*e->v1) == (*e->v2))'
  A degenerate (needle) triangle has an edge whose two endpoint vertices occupy the
  same spatial position — coincident endpoints.  MeshFix detects this via the ==
  operator on vertex coordinates and attempts an edge collapse; if collapse fails it
  unlinks the triangle directly.

Geometric signature: a triangle has two vertices placed at identical coordinates.
  The edge between them has length exactly zero — a pure needle.

Geometry (z = 0):
  v0=(0,0,0), v1=(2,0,0), v2=(2,0,0)  [v1 and v2 coincident at (2,0,0)]
  t0 = (v0, v1, v2)  — needle: edge (v1,v2) has zero length; area=0
  t1 = (v0, v1, v3) where v3=(1,2,0) — healthy neighbour to provide context
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me544",
    title="checkAndRepair::removeDegenerateTriangles NEEDLE_EDGE_COINCIDENT_ENDPOINTS: edge (v1,v2) has coincident endpoints at same coordinate; needle triangle collapse",
    defect_class="degenerate_triangle_needle_coincident_endpoints",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — base vertex
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — needle endpoint A at (2,0,0)
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — needle endpoint B at (2,0,0) [coincident with v1]
v3 = m.vertex(1.0, 2.0, 0.0)   # 3 — healthy apex for context triangle

# t0: needle triangle; edge (v1, v2) has zero length (coincident endpoints).
t0 = m.triangle(v0, v1, v2)    # 0 — needle; area=0
# t1: healthy neighbour sharing edge (v0, v1).
t1 = m.triangle(v0, v1, v3)    # 1 — healthy; area=2

# Branch 5 predicate: (*e->v1) == (*e->v2) — vertex pair (v1, v2) coincident.
m.assert_vertex_pair_distance_lt(v1, v2, 1e-9)

# t0 is exactly degenerate (area=0).
m.assert_triangle_area_lt(0, 1e-9)

# t1 is healthy.
m.assert_triangle_area_lt(1, 3.0)   # area=2 < 3

# Edge (v0, v1) shared by t0 and t1.
m.assert_edge_shared(v0, v1, 2)
