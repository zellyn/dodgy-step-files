"""Me520 — iterativeEdgeSwaps selection_exists: at least one triangle marked visited; swaps restricted to selection (Branch 1).

Basic_TMesh.iterativeEdgeSwaps branch 1: selection_exists

MeshFix `Basic_TMesh.iterativeEdgeSwaps` Branch 1 (*selection_exists*) @ line 1565:
  'if (IS_VISITED(t)) selection = 1;'
  — the algorithm scans all triangles once to detect whether any triangle has been
  marked IS_VISITED. If at least one is, the variable `selection` is set to 1 and
  subsequent edge-swap candidates are restricted to triangles within the selection.

Defect pattern: a partial-selection mesh where a subset of triangles is marked for
  Delaunay optimization. This exercises the IS_VISITED check that gates whether
  swaps apply globally or only to a selected region.

Geometry: six vertices forming two adjacent quads (each split along the same
  diagonal direction). The left quad (t0, t1) and the right quad (t2, t3) share
  edge (v2, v3). Triangles t0 and t1 represent the "selected" region (IS_VISITED).
  The interior edge (v0, v2) in the left quad is the swap candidate; the interior
  edge (v2, v3) between the quads is the shared edge.

  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(1.5,1,0), v4=(2,0,0), v5=(1,2,0)
  t0=(v0,v1,v2) — left quad lower triangle (selected)
  t1=(v1,v3,v2) — left quad upper triangle (selected)
  t2=(v1,v4,v3) — right quad lower triangle (not selected)
  t3=(v3,v5,v2) — top-center triangle

The interior edge (v1,v2) is shared by t0 and t1; (v1,v3) by t1 and t2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me520",
    title="iterativeEdgeSwaps selection_exists: partial selection of triangles restricts swaps to IS_VISITED region (Branch 1)",
    defect_class="mesh_optimization",
)

# Left quad vertices
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left corner
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — bottom center
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — left-upper
v3 = m.vertex(1.5, 1.0, 0.0)   # 3 — right-upper
v4 = m.vertex(2.0, 0.0, 0.0)   # 4 — right corner
v5 = m.vertex(1.0, 2.0, 0.0)   # 5 — top apex

# Selected region: left quad split along (v1,v2)
t0 = m.triangle(v0, v1, v2)    # 0: lower-left (IS_VISITED selection)
t1 = m.triangle(v1, v3, v2)    # 1: lower-right (IS_VISITED selection)

# Non-selected triangles completing the mesh
t2 = m.triangle(v1, v4, v3)    # 2: right quad lower
t3 = m.triangle(v3, v5, v2)    # 3: top triangle

# Interior edge (v1,v2) shared by t0 and t1 (within selection) — swap candidate.
m.assert_edge_shared(v1, v2, 2)

# Interior edge (v1,v3) shared by t1 and t2 (crosses selection boundary).
m.assert_edge_shared(v1, v3, 2)

# Interior edge (v2,v3) shared by t1 and t3.
m.assert_edge_shared(v2, v3, 2)

# Boundary edges (n=1 each).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v1, 1)
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v2, v5, 1)
