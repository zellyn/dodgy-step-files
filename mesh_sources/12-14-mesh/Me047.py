"""Me047 — compatible_orientations: non-manifold edge blocks orientation propagation.

Catalog claim: a single edge is shared by 3 triangles (non-manifold edge). CGAL
PMP.compatible_orientations Branch 2 @ line 1260 (*non_manifold_edge*) tests
is_non_manifold on each edge during the BFS propagation. When a non-manifold edge
is encountered the algorithm must return false: consistent global orientation is
impossible when a single edge is incident on 3 or more faces, because there is no
well-defined notion of "opposite halfedge" across that edge.

Defect carrier: edge (v0, v1) is shared by triangles 0, 1, and 2 — three triangles.
Triangles 3 and 4 are clean manifold neighbors that demonstrate the rest of the mesh
is otherwise fine. The non-manifold edge is the sole blocker.

Vertices: v0=(0,0,0), v1=(1,0,0) are the shared edge endpoints.
  tri0: (v0, v1, v2) where v2=(0.5,  1.0, 0.0)
  tri1: (v0, v1, v3) where v3=(0.5, -1.0, 0.0)
  tri2: (v0, v1, v4) where v4=(0.5,  0.0, 1.0)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me047",
             title="non-manifold edge shared by 3 triangles blocks compatible_orientations",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0  — shared edge start
v1 = m.vertex(1.0, 0.0, 0.0)   # 1  — shared edge end
v2 = m.vertex(0.5, 1.0, 0.0)   # 2  — fan A (above XZ plane)
v3 = m.vertex(0.5,-1.0, 0.0)   # 3  — fan B (below XZ plane)
v4 = m.vertex(0.5, 0.0, 1.0)   # 4  — fan C (above XY plane)

# Three triangles all sharing edge (v0, v1) — the non-manifold defect.
t0 = m.triangle(v0, v1, v2)    # tri 0 — above XZ plane
t1 = m.triangle(v0, v1, v3)    # tri 1 — below XZ plane
t2 = m.triangle(v0, v1, v4)    # tri 2 — above XY plane

# Assert: edge (v0,v1) is shared by exactly 3 triangles.
m.assert_edge_shared(v0, v1, 3)
