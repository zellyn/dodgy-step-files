"""Me532 — holeFilling::joinBoundaryLoops branch 3: ADJACENT_VERTICES_JUSTCONNECT.

MeshFix `holeFilling::joinBoundaryLoops` Branch 3 (*ADJACENT_VERTICES_JUSTCONNECT*) @ line 742:
  'if (gw == gvn) { EulerEdgeTriangle(…); … return bridge_edge; }'
  — gw is the immediate next neighbor of gv on the boundary; justconnect=true
    creates a single bridge triangle and returns the new edge.

Branch 3 fires when the two input boundary vertices are immediate neighbors on the
same boundary edge. With justconnect=true the algorithm short-circuits: it calls
EulerEdgeTriangle once to insert a bridge triangle and returns the new edge.

Geometry: two boundary triangles sharing a single interior edge. The two
boundary vertices v0 and v1 share boundary edge (v0,v1); gv=v0, gw=v1 are
immediate boundary neighbors. The mesh has one interior edge and four boundary
edges forming a strip.

gv=v0 and gw=v1: walking one step from v0 along the boundary reaches v1
immediately (gw == gvn) → Branch 3 fires; one EulerEdgeTriangle call.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me532",
             title="joinBoundaryLoops_ADJACENT_VERTICES_JUSTCONNECT: gw is immediate boundary neighbor; Branch 3 inserts single triangle",
             defect_class="joinBoundaryLoops_adjacent_vertices_justconnect")

# Minimal strip: two triangles sharing one interior edge.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — gv (boundary)
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — gw (boundary, immediate neighbor of gv)
v2 = m.vertex(1.0, 1.0, 0.0)   # 2 — top-left apex
v3 = m.vertex(1.0, -1.0, 0.0)  # 3 — bottom-right apex

# Two triangles sharing the interior edge (v0, v1).
t0 = m.triangle(v0, v1, v2)   # 0 — upper triangle
t1 = m.triangle(v0, v3, v1)   # 1 — lower triangle (gv=v0, gw=v1 adjacent here)

# Interior edge shared by 2 triangles.
m.assert_edge_shared(v0, v1, 2)   # interior (shared edge; gv-gw immediate boundary pair)

# Four boundary edges (n=1 each).
m.assert_edge_shared(v0, v2, 1)   # boundary
m.assert_edge_shared(v1, v2, 1)   # boundary
m.assert_edge_shared(v0, v3, 1)   # boundary
m.assert_edge_shared(v1, v3, 1)   # boundary

# Boundary loop: v0, v2, v1, v3 (single loop, all on boundary).
m.assert_hole_boundary([v0, v2, v1, v3])

# Euler: V=4, E=5, F=2, chi=1 (open strip).
m.assert_euler_characteristic(4, 5, 2, 1)
