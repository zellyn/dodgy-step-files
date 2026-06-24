"""Me1198 — keep_largest_connected_components dry_run_mode:
  dry_run=true causes function to count removals without modifying mesh (Branch 3).

CGAL PMP `PMP.keep_largest_connected_components` Branch 3 (*dry_run_mode*)
  @ line 419:
  'if (dry_run) return nb_removed;' —
  When the dry_run named parameter is set to true, the function computes which
  components would be removed and how many, but returns early without actually
  modifying the mesh. Branch 3 fires when the dry_run parameter is detected.

Defect pattern: a mesh with 3 connected components of sizes 4, 2, 1 triangles.
  Calling keep_largest_connected_components(mesh, 1, np::dry_run(true)) should
  return 2 (the two smaller components) without actually removing them. Branch 3
  fires at the dry-run guard, skipping the remove_connected_components call.
  The mesh topology is unchanged after the dry-run call.

Geometry: same three-component topology as Me1197 (4-tri, 2-tri, 1-tri).
  The fixture demonstrates the dry-run path: mesh must be left intact.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1198",
    title="keep_largest_connected_components dry_run_mode: dry_run=true returns count of removable components without modifying mesh; 3 components, keep 1 largest (Branch 3)",
    defect_class="self_intersection",
)

# Component A: 4-triangle fan (largest)
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — center
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3
v4 = m.vertex(0.0, -1.0, 0.0)  # 4

t0 = m.triangle(v0, v1, v2)    # 0
t1 = m.triangle(v0, v2, v3)    # 1
t2 = m.triangle(v0, v3, v4)    # 2
t3 = m.triangle(v0, v4, v1)    # 3

# Component B: 2-triangle strip (medium)
v5 = m.vertex(10.0, 0.0, 0.0)  # 5
v6 = m.vertex(11.0, 0.0, 0.0)  # 6
v7 = m.vertex(10.5, 1.0, 0.0)  # 7
v8 = m.vertex(11.5, 1.0, 0.0)  # 8

t4 = m.triangle(v5, v6, v7)    # 4
t5 = m.triangle(v6, v8, v7)    # 5

# Component C: 1-triangle isolated (smallest)
v9  = m.vertex(20.0, 0.0, 0.0)  # 9
v10 = m.vertex(21.0, 0.0, 0.0)  # 10
v11 = m.vertex(20.5, 1.0, 0.0)  # 11

t6 = m.triangle(v9, v10, v11)   # 6

# Three components disconnected
m.assert_triangle_not_reachable_from(t4, t0)
m.assert_triangle_not_reachable_from(t6, t0)
m.assert_triangle_not_reachable_from(t6, t4)

# After dry-run, all triangles remain in the mesh
# (dry_run=true does not modify the mesh, so all components still present)
# Component A fan interior
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v0, v4, 2)
# Component A boundary
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v1, v4, 1)
# Component B
m.assert_edge_shared(v5, v6, 1)
m.assert_edge_shared(v5, v7, 1)
m.assert_edge_shared(v6, v7, 2)
m.assert_edge_shared(v6, v8, 1)
m.assert_edge_shared(v7, v8, 1)
# Component C
m.assert_edge_shared(v9, v10, 1)
m.assert_edge_shared(v9, v11, 1)
m.assert_edge_shared(v10, v11, 1)

# V=12, E=16, F=7, chi=3
m.assert_euler_characteristic(12, 16, 7, 3)
