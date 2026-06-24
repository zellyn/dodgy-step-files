"""Me571 — Basic_TMesh.invertSelection branch 2: component_invert_direction — bool unmark = IS_VISITED(t0); pre-marked seed → unmark mode.

MeshFix `Basic_TMesh.invertSelection` Branch 2 (*component_invert_direction*) @ line 748:
  'bool unmark = IS_VISITED(t0);'
  — the direction of the BFS toggle is determined by whether the seed t0 is
  already marked (VISITED). When IS_VISITED(t0) is true, unmark=true and the
  BFS will clear marks from all same-state (visited) triangles in the component.
  Branch 2 fires whenever a seed is provided and the algorithm reads t0's
  IS_VISITED bit to determine the direction.

Defect pattern: a small closed-disk mesh with a pre-marked seed triangle.
  The seed (t0) is pre-marked (IS_VISITED = true). When invertSelection is called
  with t0, it reads unmark=true (Branch 2), then BFS unmarks all VISITED triangles
  in the component, leaving them all unvisited afterward.

Geometry (fan of four triangles around a central vertex, closed):
  v0=(0,0,0) hub, v1=(1,0,0), v2=(0,1,0), v3=(-1,0,0), v4=(0,-1,0)
  t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4), t3=(v0,v4,v1)
  Each consecutive pair shares an edge through v0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me571",
    title="Basic_TMesh.invertSelection component_invert_direction: IS_VISITED(t0)=true → unmark=true; BFS unmarks pre-marked seed component (Branch 2)",
    defect_class="mesh_selection_toggle",
)

v0 = m.vertex(0.0,  0.0, 0.0)  # 0 — hub vertex
v1 = m.vertex(1.0,  0.0, 0.0)  # 1
v2 = m.vertex(0.0,  1.0, 0.0)  # 2
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3
v4 = m.vertex(0.0, -1.0, 0.0)  # 4

# Four triangles forming a fan around v0 (closed pinwheel).
t0 = m.triangle(v0, v1, v2)  # 0: seed — IS_VISITED=true → unmark=true (Branch 2)
t1 = m.triangle(v0, v2, v3)  # 1
t2 = m.triangle(v0, v3, v4)  # 2
t3 = m.triangle(v0, v4, v1)  # 3

# Interior edges shared by pairs of triangles (n=2).
m.assert_edge_shared(v0, v1, 2)  # t0-t3
m.assert_edge_shared(v0, v2, 2)  # t0-t1
m.assert_edge_shared(v0, v3, 2)  # t1-t2
m.assert_edge_shared(v0, v4, 2)  # t2-t3

# Outer boundary edges (n=1).
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v1, 1)

# Euler: V=5, E=8, F=4, chi=1 (open disk — pinwheel with boundary).
m.assert_euler_characteristic(5, 8, 4, 1)
