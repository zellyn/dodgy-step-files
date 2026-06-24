"""Me980 — merge_reversible_connected_components component_area_filter: tiny
  component area below threshold triggers mergeable marking (Branch 1).

CGAL PMP `PMP.merge_reversible_connected_components` Branch 1
  (*component_area_filter*) @ line 1050:
  'if (component.area() < area_threshold) { mark_as_mergeable(component); }'
  — the algorithm iterates over each connected component and compares its
  area against a size threshold. Components whose area is below the threshold
  are flagged as reversible/mergeable candidates. This branch fires when at
  least one component is small enough to fall under the threshold.

Defect pattern: a mesh with two disconnected connected components. Component A
  is a large triangle (area ≈ 0.5 sq units). Component B is a degenerate-scale
  micro-triangle (area ≈ 5e-9 sq units), far below any reasonable area
  threshold. The mesh has no shared edges between CCs — CC-B is geometrically
  isolated. The component_area_filter branch fires on CC-B, marking it as a
  merge candidate.

Geometry:
  CC A: a0=(0,0,0), a1=(1,0,0), a2=(0,1,0)
        t0=(a0,a1,a2) — area = 0.5
  CC B: b0=(10,0,0), b1=(10,1e-4,0), b2=(10,0,1e-4)
        t1=(b0,b1,b2) — area ≈ 5e-9 (micro-triangle)
  CCs are disjoint: no shared edges, 30+ units apart horizontally.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me980",
    title="merge_reversible_connected_components component_area_filter: micro-triangle CC-B (area≈5e-9) below threshold; marked as mergeable (Branch 1)",
    defect_class="multi_component_area_imbalance",
)

# CC A: large triangle in the XY plane.
a0 = m.vertex(0.0, 0.0, 0.0)   # 0 — origin corner
a1 = m.vertex(1.0, 0.0, 0.0)   # 1 — x-corner
a2 = m.vertex(0.0, 1.0, 0.0)   # 2 — y-corner
t0 = m.triangle(a0, a1, a2)    # 0: large CCW triangle; area = 0.5

# CC B: micro-triangle far away — area ≈ 5e-9 sq units.
b0 = m.vertex(10.0, 0.0,    0.0)     # 3 — micro CC origin
b1 = m.vertex(10.0, 1e-4,   0.0)     # 4 — micro y-offset
b2 = m.vertex(10.0, 0.0,    1e-4)    # 5 — micro z-offset
t1 = m.triangle(b0, b1, b2)          # 1: micro-triangle; area ≈ 5e-9

# CC B is geometrically isolated from CC A.
m.assert_triangle_not_reachable_from(1, 0)

# CC B has area well below any reasonable threshold.
m.assert_triangle_area_lt(1, 1e-7)

# Euler: two open triangles — each is V=3,E=3,F=1,chi=1; combined V=6,E=6,F=2,chi=2.
m.assert_euler_characteristic(6, 6, 2, 2)
