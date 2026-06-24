"""Me584 — createSubMeshFromSelection edge_adjacency_boundary: selection boundary edge; sub-mesh adjacency set to NULL on outside (Branch 5).

Basic_TMesh.createSubMeshFromSelection branch 5: edge_adjacency_boundary

Source method: `Basic_TMesh.createSubMeshFromSelection` @ line 865
Branch condition: For each edge in the extracted sub-mesh, the algorithm checks
`IS_VISITED(e->t1)` and `IS_VISITED(e->t2)` to decide whether to link the sub-mesh
edge to its neighboring triangle or set the adjacency to NULL.

When exactly one of the two adjacent original triangles is in the selection, the
edge becomes a boundary in the sub-mesh (adjacency = NULL for the outside direction).
This is the selection-boundary edge case: the edge's t1 is visited but t2 is not
(or vice versa), so the sub-mesh edge becomes a boundary edge even though it was
interior in the original mesh.

Defect pattern: a 2×2 grid of 4 triangles where only 2 triangles (one column)
are selected. The shared edge between the selected column and the unselected
column is the selection-boundary edge: it is interior in the original mesh (n=2)
but becomes a boundary edge in the sub-mesh because the opposite triangle is not
visited.

Geometric signature:
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0)
  v3=(0,1,0), v4=(1,1,0), v5=(2,1,0)

  Two rows of two triangles (upper-left pair and upper-right pair):
    t0=(v0,v1,v3) — unvisited (left column)
    t1=(v1,v4,v3) — unvisited (left column)
    t2=(v1,v2,v4) — visited (right column, BFS seed)
    t3=(v2,v5,v4) — visited (right column)

  Edge (v1,v4) is shared by t1 (unvisited) and t2 (visited) → selection-boundary
  edge. In the sub-mesh of {t2,t3} this edge becomes NULL on the t1 side.

  In the full mesh, edge (v1,v4) is interior (n=2). The sub-mesh boundary at
  this edge is what Branch 5 explicitly handles.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me584",
    title="createSubMeshFromSelection edge_adjacency_boundary: interior edge (v1,v4) is selection boundary; sub-mesh adjacency becomes NULL toward unvisited t1 (Branch 5)",
    defect_class="mesh_selection",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — bottom-left
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — bottom-center (selection boundary vertex)
v2 = m.vertex(2.0, 0.0, 0.0)  # 2 — bottom-right
v3 = m.vertex(0.0, 1.0, 0.0)  # 3 — top-left
v4 = m.vertex(1.0, 1.0, 0.0)  # 4 — top-center (selection boundary vertex)
v5 = m.vertex(2.0, 1.0, 0.0)  # 5 — top-right

# Left column — unvisited.
t0 = m.triangle(v0, v1, v3)  # 0: unvisited
t1 = m.triangle(v1, v4, v3)  # 1: unvisited

# Right column — visited (the selected sub-mesh).
t2 = m.triangle(v1, v2, v4)  # 2: visited (BFS seed)
t3 = m.triangle(v2, v5, v4)  # 3: visited

# The critical selection-boundary edge: interior in the full mesh (n=2),
# becomes a boundary in the extracted sub-mesh because t1 is unvisited.
m.assert_edge_shared(v1, v4, 2)  # shared by t1 (unvisited) and t2 (visited)

# Other interior edges (within each column).
m.assert_edge_shared(v1, v3, 2)  # t0 and t1 — interior to left column
m.assert_edge_shared(v2, v4, 2)  # t2 and t3 — interior to right column

# Boundary (outer) edges — each shared by exactly 1 triangle.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v5, 1)
m.assert_edge_shared(v4, v5, 1)

# Euler: V=6, E=9, F=4, chi=1 (open disk).
m.assert_euler_characteristic(6, 9, 4, 1)
