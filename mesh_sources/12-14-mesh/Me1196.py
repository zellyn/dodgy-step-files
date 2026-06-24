"""Me1196 — keep_largest_connected_components component_count_mismatch:
  desired_num_to_keep > actual number of connected components; returns 0 (Branch 1).

CGAL PMP `PMP.keep_largest_connected_components` Branch 1 (*component_count_mismatch*)
  @ line 401:
  'if (nb_components <= nb_components_to_keep) return 0;' —
  When the caller requests keeping more connected components than actually exist
  in the mesh, no removal is needed and the function returns 0 immediately.
  Branch 1 fires when nb_components_to_keep >= total component count.

Defect pattern: a mesh with exactly 2 connected components (a triangle and an
  isolated quad), and the caller requests keeping 3 or more — more than exist.
  nb_components=2 <= nb_components_to_keep=3, so Branch 1 fires: return 0
  (no components removed, mesh unchanged).

Geometry: two separate triangles (two disconnected components).
  Component A: t0=(v0,v1,v2) — small triangle at origin
  Component B: t1=(v3,v4,v5) — triangle far away at x=10
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1196",
    title="keep_largest_connected_components component_count_mismatch: desired_num=3 > nb_components=2; Branch 1 fires returning 0 removed components (Branch 1)",
    defect_class="self_intersection",
)

# Component A: small triangle at origin
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

# Component B: triangle far away
v3 = m.vertex(10.0, 0.0, 0.0)  # 3
v4 = m.vertex(11.0, 0.0, 0.0)  # 4
v5 = m.vertex(10.5, 1.0, 0.0)  # 5

t0 = m.triangle(v0, v1, v2)    # 0: component A
t1 = m.triangle(v3, v4, v5)    # 1: component B

# These two components are completely disconnected
m.assert_triangle_not_reachable_from(t1, t0)

# Component A edges
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)

# Component B edges
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v4, v5, 1)

# V=6, E=6, F=2, chi=2 (two separate discs)
m.assert_euler_characteristic(6, 6, 2, 2)
