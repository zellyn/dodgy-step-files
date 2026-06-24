"""Me581 — createSubMeshFromSelection seed_provided: BFS from visited seed collects all visited neighbors (Branch 2).

Basic_TMesh.createSubMeshFromSelection branch 2: seed_provided

Source method: `Basic_TMesh.createSubMeshFromSelection` @ line 801
Branch condition: `t0 != NULL && IS_VISITED(t0)` — the caller provided a seed
triangle that IS in the IS_VISITED selection. The algorithm performs a BFS flood
fill from t0, collecting all transitively reachable visited triangles (via
triList.appendHead and neighbor traversal).

Defect pattern: a connected strip of 5 triangles where exactly 3 form a
contiguous visited region. The caller passes t1 (the leftmost visited triangle)
as the seed. BFS from t1 visits t2 and t3 via shared edges, collecting all 3
visited triangles into the sub-mesh. Unvisited triangles t0 and t4 stop the BFS
at the selection boundary.

Geometric signature:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(2,0,0), v4=(1.5,1,0), v5=(3,0,0)
  t0=(v0,v1,v2) — unvisited
  t1=(v1,v3,v2) — visited (BFS seed)
  t2=(v1,v3,v4) — visited (wait: rethink)

  Simpler: 5 triangles in a fan around a central vertex.
  v0=(0,0,0) hub, v1..v5 on the rim.
  t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4), t3=(v0,v4,v5) — 4 triangles
  Visited: t1, t2, t3 (contiguous). Unvisited: t0.
  Seed = t1 (leftmost visited). BFS collects t2, t3 via (v0,v3) and (v0,v4).

  The selection boundary between t0 and t1 (edge v0,v2) would produce a
  boundary edge in the sub-mesh (adjacent unvisited triangle t0 → sub-mesh
  loses the t2 adjacency on that edge).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me581",
    title="createSubMeshFromSelection seed_provided: BFS from visited seed t1 collects contiguous visited region {t1,t2,t3}; unvisited t0 stops flood fill (Branch 2)",
    defect_class="mesh_selection",
)

# Hub vertex at origin, 5 rim vertices sweeping counter-clockwise.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — hub
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — rim right
v2 = m.vertex(1.5, 1.5, 0.0)   # 2 — rim upper-right
v3 = m.vertex(0.0, 2.0, 0.0)   # 3 — rim top
v4 = m.vertex(-1.5, 1.5, 0.0)  # 4 — rim upper-left
v5 = m.vertex(-2.0, 0.0, 0.0)  # 5 — rim left

# Four triangles in a fan around hub v0.
t0 = m.triangle(v0, v1, v2)  # 0: unvisited — left of selection
t1 = m.triangle(v0, v2, v3)  # 1: visited (BFS seed provided by caller)
t2 = m.triangle(v0, v3, v4)  # 2: visited (reachable from t1 via edge v0,v3)
t3 = m.triangle(v0, v4, v5)  # 3: visited (reachable from t2 via edge v0,v4)

# Hub spoke edges — each spoke (v0,vN) shared by the two adjacent fan triangles.
m.assert_edge_shared(v0, v1, 1)  # boundary: only t0
m.assert_edge_shared(v0, v2, 2)  # t0 and t1 — selection boundary edge
m.assert_edge_shared(v0, v3, 2)  # t1 and t2 — interior to selection
m.assert_edge_shared(v0, v4, 2)  # t2 and t3 — interior to selection
m.assert_edge_shared(v0, v5, 1)  # boundary: only t3

# Rim edges — each shared by exactly 1 triangle (outer boundary of the fan).
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)

# The selection-boundary edge (v0, v2) separates unvisited t0 from visited t1.
# In the extracted sub-mesh, the adjacency through (v0,v2) from t1 becomes NULL.
# In the full mesh this edge is shared by t0 and t1 (n=2 above).

# Euler: V=6, E=9, F=4, chi=1 (open fan, genus 0).
m.assert_euler_characteristic(6, 9, 4, 1)
