"""Me283 — checkGeometry_memory_alloc_fail_edges: coincident edge pair triggers edge-alloc guard (Branch 4).

MeshFix `checkAndRepair::checkGeometry` Branch 4 (*MEMORY_ALLOCATION_FAILURE_EDGES*) @ line 220:
  Edge array allocation for coincident-edge check fails; function skips the
  coincident-edge scan and continues. The same coincident-edge geometry would be
  caught by Branch 5 (COINCIDENT_EDGES) if memory is available.

Geometry: two triangles where the edge geometry is spatially coincident but vertex
indices differ. Vertex v0=(0,0,0) and v3=(0,0,0) are coincident; v1=(1,0,0) and
v4=(1,0,0) are coincident. Edge (v0,v1) in triangle t0 and edge (v3,v4) in triangle t1
are spatially identical — same endpoints by coordinate, different by index.
Branch 4 fires when ExtTriMesh::newEdges fails to allocate the sort buffer for
this coincident-edge detection.

Triangle t0: v0=(0,0,0), v1=(1,0,0), v2=(0,1,0).
Triangle t1: v3=(0,0,0), v4=(1,0,0), v5=(0,-1,0) — shares same edge geometry as t0 via coincident verts.

Sources: MeshFix `checkAndRepair::checkGeometry` lines 217–224; MESH_HEAL_COVERAGE.md.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me283",
    title="checkGeometry_memory_alloc_fail_edges: coincident edge pair, edge alloc guard (Branch 4)",
    defect_class="coincident_edges",
)

# Triangle 0: canonical position.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2
m.triangle(v0, v1, v2)          # t0

# Triangle 1: v3 coincides with v0, v4 coincides with v1 — different indices.
# Edge (v3,v4) is spatially identical to edge (v0,v1).
v3 = m.vertex(0.0, 0.0, 0.0)   # 3 — coincides with v0
v4 = m.vertex(1.0, 0.0, 0.0)   # 4 — coincides with v1
v5 = m.vertex(0.0, -1.0, 0.0)  # 5
m.triangle(v3, v4, v5)          # t1

# Assert: vertex pairs are coincident (confirms the endpoint coincidence).
m.assert_vertex_pair_distance_lt(v0, v3, 1e-12)
m.assert_vertex_pair_distance_lt(v1, v4, 1e-12)

# Assert: the two edges (v0,v1) and (v3,v4) are spatially coincident.
m.assert_edge_pair_coincident((v0, v1), (v3, v4))
