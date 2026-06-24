"""Me465 — selectConnectedComponent mark_and_count: MARK_VISIT(t); ns++ completes BFS.

Catalog claim: Basic_TMesh.selectConnectedComponent Branch 6 @ line 1082
(*mark_and_count*): at the end of each BFS iteration (after the t1/t2/t3 enqueue
checks), the current triangle is marked visited and the component counter incremented:
  `MARK_VISIT(t); ns++;`
This fires for every triangle that passes the `!IS_VISITED(t)` check — i.e., for
every triangle that is actually processed and added to the connected component.

Branch 6 represents the "commit" step of the BFS: the triangle is stamped as visited
and the count ns goes up by one. For a mesh with N triangles in one component, this
branch fires exactly N times. This fixture uses a 4-triangle mesh to demonstrate
that ns reaches 4 after BFS completes.

Geometric signature: four triangles in a 2×2 grid arrangement (two pairs of triangles
sharing a long diagonal), forming a single connected component. Every triangle gets
processed in BFS order; MARK_VISIT + ns++ fires 4 times (once per triangle).

  v0=(0,0) v1=(1,0) v2=(2,0)
  v3=(0,1) v4=(1,1) v5=(2,1)

  t0 = (v0, v1, v3)  — lower-left
  t1 = (v1, v4, v3)  — upper-left (shares diagonal v1,v3 with t0)
  t2 = (v1, v2, v4)  — lower-right (shares edge v1,v4 with t1)
  t3 = (v2, v5, v4)  — upper-right (shares diagonal v2,v4 with t2)

BFS from t0 marks all 4 triangles; ns = 4 at termination. Branch 6 fires 4 times.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me465",
             title="selectConnectedComponent mark_and_count: MARK_VISIT(t);ns++ fires for each BFS-processed triangle (ns=4)",
             defect_class="disconnected_components")

# Six vertices forming a 2×2 quad grid.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(2.0, 0.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)
v4 = m.vertex(1.0, 1.0, 0.0)
v5 = m.vertex(2.0, 1.0, 0.0)

# Four triangles forming a connected 2×2 grid (two quads, each split diagonally).
t0 = m.triangle(v0, v1, v3)   # 0: lower-left; BFS root; MARK_VISIT fires 1st
t1 = m.triangle(v1, v4, v3)   # 1: upper-left; shares (v1,v3) with t0; MARK_VISIT fires 2nd
t2 = m.triangle(v1, v2, v4)   # 2: lower-right; shares (v1,v4) with t1; MARK_VISIT fires 3rd
t3 = m.triangle(v2, v5, v4)   # 3: upper-right; shares (v2,v4) with t2; MARK_VISIT fires 4th

# Interior shared edges (each exactly 2 triangles).
m.assert_edge_shared(v1, v3, 2)   # shared by t0 and t1 (left quad diagonal)
m.assert_edge_shared(v1, v4, 2)   # shared by t1 and t2 (vertical center)
m.assert_edge_shared(v2, v4, 2)   # shared by t2 and t3 (right quad diagonal)

# Boundary edges (each exactly 1 triangle).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v2, v5, 1)
m.assert_edge_shared(v1, v2, 1)

# All four triangles form a single connected component — BFS visits all 4 (ns == 4).
# Adjacent triangle pairs share edges: t0↔t1, t1↔t2, t2↔t3.
m.assert_adjacent_triangles_normal_dot_gt(t0, t1, 0.9)   # coplanar, same z-up normal
m.assert_adjacent_triangles_normal_dot_gt(t1, t2, 0.9)
m.assert_adjacent_triangles_normal_dot_gt(t2, t3, 0.9)

# Euler: V=6, E=9 (3 interior + 6 boundary), F=4, chi = 6 - 9 + 4 = 1 (open disk).
m.assert_euler_characteristic(v=6, e=9, f=4, chi=1)
