"""Me284 — checkGeometry_coincident_edges: two mesh edges at identical coordinates (Branch 5).

MeshFix `checkAndRepair::checkGeometry` Branch 5 (*COINCIDENT_EDGES*) @ line 226:
  After lex-sorting edges by vertex coordinates, two adjacent entries share the same
  vertex pair positions (different half-edge objects, same geometry). checkGeometry
  marks edge v1 as defective and flags a geometry issue.

Geometry: two triangles that share coincident edge geometry via spatially identical
but topologically distinct vertices. v0=(0,0,0) and v3=(0,0,0) are at the same
position; v1=(1,0,0) and v4=(1,0,0) are at the same position. In the half-edge
structure, edge (v0,v1) and edge (v3,v4) are two distinct edge objects but map to
the same coordinate pair — detected as coincident during the sorted-edge scan.

Triangle t0: v0=(0,0,0), v1=(1,0,0), v2=(0,1,0) — upper triangle.
Triangle t1: v3=(0,0,0), v4=(1,0,0), v5=(0,-1,0) — lower triangle; edge (v3,v4) == (v0,v1) geometrically.

Sources: MeshFix `checkAndRepair::checkGeometry` lines 223–230; MESH_HEAL_COVERAGE.md.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me284",
    title="checkGeometry_coincident_edges: two spatially identical edges with different vertex indices (Branch 5)",
    defect_class="coincident_edges",
)

# Triangle 0: upper triangle.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2
m.triangle(v0, v1, v2)          # t0 — edge (0,1) on XZ plane

# Triangle 1: lower triangle — v3 and v4 duplicate v0 and v1 coordinates exactly.
v3 = m.vertex(0.0, 0.0, 0.0)   # 3 — same position as v0
v4 = m.vertex(1.0, 0.0, 0.0)   # 4 — same position as v1
v5 = m.vertex(0.0, -1.0, 0.0)  # 5 — below X axis
m.triangle(v3, v4, v5)          # t1 — edge (3,4) coincides with edge (0,1)

# Assert: coincident vertex pairs that anchor the coincident edges.
m.assert_vertex_pair_distance_lt(v0, v3, 1e-12)
m.assert_vertex_pair_distance_lt(v1, v4, 1e-12)

# Assert: edge (v0,v1) and edge (v3,v4) are spatially coincident.
m.assert_edge_pair_coincident((v0, v1), (v3, v4))
