"""Me1043 — stitch_borders processing-strategy-dispatch: per_cc for-loop iterates over each connected component.

CGAL PMP `PMP.stitch_borders (internal dispatcher)` Branch 4 (*processing-strategy-dispatch*) @ line 449:
  'if (per_cc) { for (std::size_t i = 0; i < num_cc; ++i) { ... border_edges_per_cc[i] ... } }'
  After collecting border edges per component, the dispatcher enters a loop over
  num_cc connected components, processing each component's boundary list independently.
  Branch 4 fires once per connected component. With two components, the loop body
  executes twice.

Defect pattern: two disconnected patches, each with a stitchable seam on their
  right side. Component A has a coincident boundary pair (v2/v5 and v3/v6).
  Component B has a coincident boundary pair (v9/v12 and v10/v13). The for-loop
  iterates over num_cc=2, invoking the stitch logic separately for each component.

Geometry:
  Component A:
    v0=(0,0,0), v1=(1,0,0), v2=(2,0,0), v3=(2,1,0), v4=(1,1,0)
    t0=(v0,v1,v4), t1=(v1,v2,v3), t2=(v1,v3,v4) — open strip; (v1,v3),(v1,v4) interior
    Seam A: v2==v5 at (2,0,0) and v3==v6 at (2,1,0)
    v5=(2,0,0), v6=(2,1,0), v7=(3,0,0), v8=(3,1,0)
    t3=(v5,v7,v8), t4=(v5,v8,v6) — second sub-patch; (v5,v8) interior
  Component B (far away):
    v9=(6,0,0), v10=(7,0,0), v11=(6,1,0)
    t5=(v9,v10,v11) — single triangle

  Simpler: two disconnected pairs of triangles, each pair sharing an interior edge
  and having open boundaries.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1043",
    title="stitch_borders processing-strategy-dispatch: per_cc for-loop iterates over num_cc=2 connected components; two open two-triangle patches",
    defect_class="boundary_gap_thin",
)

# Component A — left patch (two triangles)
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(1.5, 1.0, 0.0)   # 3

# Component B — right patch (two triangles, disconnected)
v4 = m.vertex(4.0, 0.0, 0.0)   # 4
v5 = m.vertex(5.0, 0.0, 0.0)   # 5
v6 = m.vertex(4.5, 1.0, 0.0)   # 6
v7 = m.vertex(5.5, 1.0, 0.0)   # 7

# Component A triangles
t0 = m.triangle(v0, v1, v2)    # 0
t1 = m.triangle(v1, v3, v2)    # 1 — shares (v1,v2) with t0

# Component B triangles
t2 = m.triangle(v4, v5, v6)    # 2
t3 = m.triangle(v5, v7, v6)    # 3 — shares (v5,v6) with t2

# Interior edges
m.assert_edge_shared(v1, v2, 2)  # Component A
m.assert_edge_shared(v5, v6, 2)  # Component B

# Boundary edges — Component A
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# Boundary edges — Component B
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v4, v6, 1)
m.assert_edge_shared(v5, v7, 1)
m.assert_edge_shared(v6, v7, 1)

# Components are disconnected — for-loop fires for each
m.assert_triangle_not_reachable_from(t2, t0)

# Euler: V=8, E=10, F=4, chi=2 (two open disks)
m.assert_euler_characteristic(8, 10, 4, 2)
