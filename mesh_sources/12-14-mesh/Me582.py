"""Me582 — createSubMeshFromSelection no_seed: global scan of all visited triangles for multi-component visited mesh (Branch 3).

Basic_TMesh.createSubMeshFromSelection branch 3: no_seed

Source method: `Basic_TMesh.createSubMeshFromSelection` @ line 827
Branch condition: `t0 == NULL` — no seed triangle is provided. The algorithm
falls into the else branch and performs a global FOREACHTRIANGLE scan, collecting
every triangle flagged IS_VISITED into the sub-mesh, regardless of connectivity.
This is the multi-component path: two or more disconnected visited patches are
all captured into one sub-mesh.

Defect pattern: two separate triangle pairs, each pair sharing one interior edge,
with no edges connecting the two pairs. Both pairs are marked IS_VISITED. The
caller passes NULL as the seed. Branch 3 fires: the algorithm iterates every
triangle and collects all 4 visited triangles.

The vertex_pair_no_shared_triangle assertion between a vertex from the first pair
and a vertex from the second pair confirms the disconnection between the two
visited components.

Geometric signature:
  Component A — two triangles sharing edge (v0,v2):
    v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0)
    v3=(−1,0,0)
    tA0=(v0,v1,v2), tA1=(v3,v0,v2)

  Component B — two triangles sharing edge (v4,v6), far from Component A:
    v4=(10,0,0), v5=(11,0,0), v6=(10.5,1,0)
    v7=(9,0,0)
    tB0=(v4,v5,v6), tB1=(v7,v4,v6)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me582",
    title="createSubMeshFromSelection no_seed: NULL seed triggers global FOREACHTRIANGLE scan; two disconnected visited components both collected into sub-mesh (Branch 3)",
    defect_class="mesh_selection",
)

# Component A — two triangles sharing interior edge (v0, v2).
v0 = m.vertex(0.0,   0.0, 0.0)  # 0
v1 = m.vertex(1.0,   0.0, 0.0)  # 1
v2 = m.vertex(0.5,   1.0, 0.0)  # 2
v3 = m.vertex(-1.0,  0.0, 0.0)  # 3

tA0 = m.triangle(v0, v1, v2)  # 0: visited (Component A)
tA1 = m.triangle(v3, v0, v2)  # 1: visited (Component A)

# Component B — two triangles sharing interior edge (v4, v6), far from A.
v4 = m.vertex(10.0,  0.0, 0.0)  # 4
v5 = m.vertex(11.0,  0.0, 0.0)  # 5
v6 = m.vertex(10.5,  1.0, 0.0)  # 6
v7 = m.vertex(9.0,   0.0, 0.0)  # 7

tB0 = m.triangle(v4, v5, v6)  # 2: visited (Component B)
tB1 = m.triangle(v7, v4, v6)  # 3: visited (Component B)

# Component A interior edge — shared by tA0 and tA1.
m.assert_edge_shared(v0, v2, 2)

# Component A boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v3, v0, 1)
m.assert_edge_shared(v3, v2, 1)

# Component B interior edge — shared by tB0 and tB1.
m.assert_edge_shared(v4, v6, 2)

# Component B boundary edges.
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, v6, 1)
m.assert_edge_shared(v7, v4, 1)
m.assert_edge_shared(v7, v6, 1)

# Cross-component disconnection: v1 (Component A) and v5 (Component B)
# do not appear together in any triangle → confirms two separate components.
m.assert_vertex_pair_no_shared_triangle(v1, v5)

# Euler per component: each is V=4, E=5, F=2, chi=1 (open disk).
# Combined mesh: V=8, E=10, F=4, chi=2 (two disjoint open disks).
m.assert_euler_characteristic(8, 10, 4, 2)
