"""Me235 — topTriangle_highest_vertex_search: vertex with max z found and becomes hv.

MeshFix `Basic_TMesh.topTriangle` Branch 6 (*highest_vertex_search*) @ line 1717:
  '(az = v->z) > Mz' — vertex z exceeds current max; update hv and Mz.

After collecting all vertices into vlist, topTriangle scans the list for the
vertex with the greatest z-coordinate. Branch 6 fires each time a vertex beats
the running maximum. With four vertices at distinct z-levels, Branch 6 fires
three times as each new maximum is found.

Geometry: four vertices on a staircase — z=0, z=1, z=2, z=3:
  v0=(0,0,0) z=0 (initial Mz=-inf → Branch 6 fires)
  v1=(1,0,1) z=1 (> 0 → Branch 6 fires again)
  v2=(2,0,2) z=2 (> 1 → Branch 6 fires again)
  v3=(3,0,3) z=3 (> 2 → Branch 6 fires; hv=v3 final)
  t0=(v0,v1,v3), t1=(v1,v2,v3)   — two triangles connecting all four vertices.

After the scan, hv=v3 (z=3 is the maximum). The geometry confirms v3 is highest
and will be the anchor for steepest-edge selection (Branches 7–8).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me235",
             title="topTriangle_highest_vertex_search: four staircase z-levels; v3 (z=3) becomes hv",
             defect_class="topTriangle_highest_vertex_search")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — z=0; first Mz seed
v1 = m.vertex(1.0, 0.0, 1.0)   # 1 — z=1; beats Mz=0 (Branch 6 fires)
v2 = m.vertex(2.0, 0.0, 2.0)   # 2 — z=2; beats Mz=1 (Branch 6 fires)
v3 = m.vertex(3.0, 0.0, 3.0)   # 3 — z=3; beats Mz=2 (Branch 6 fires); final hv

t0 = m.triangle(v0, v1, v3)   # 0
t1 = m.triangle(v1, v2, v3)   # 1 — shares edge (v1,v3) with t0

# Interior edge (v1,v3) shared by both triangles.
m.assert_edge_shared(v1, v3, 2)

# Boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)

# Euler: V=4, E=5, F=2, chi=1.
m.assert_euler_characteristic(4, 5, 2, 1)

# v3 (index 3) has the highest z-coordinate in the mesh.
# Its z=3 is strictly greater than z=2 (v2), z=1 (v1), z=0 (v0).
m.assert_vertex_pair_distance_lt(v2, v3, 2.0)   # v2→v3 step is sqrt(1+1)~1.4
