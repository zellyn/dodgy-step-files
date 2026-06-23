"""Me171 — orient_component_init: first polygon seeded as oriented, pushed to DFS stack.

Catalog claim: a three-triangle strip where the leftmost triangle is the seed
polygon that Branch 2 (*component_init*) marks as oriented and pushes onto the
DFS stack. Without this initialization step, the entire DFS (Branch 3) would
never start.

Geometric signature: three CCW triangles sharing edges in a horizontal strip.
Triangle 0 is the seed (first polygon found). Triangles 1 and 2 are reachable
via shared edges from triangle 0, so they are oriented by the DFS — not by
polygon_scan. The seed-selection + stack-push is Branch 2 (*component_init*).

Defect carrier: triangle 1 has reversed (CW) winding, creating an
inconsistent-winding pair with triangle 0. The orient algorithm's Branch 2
must seed on triangle 0; DFS then reaches triangle 1 and reverses it.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me171",
             title="orient component_init: seed polygon pushed to DFS stack, starts orientation propagation",
             defect_class="inconsistent_winding")

# Horizontal strip of 3 triangles in XY plane.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(2.0, 0.0, 0.0)
v3 = m.vertex(3.0, 0.0, 0.0)
v4 = m.vertex(0.5, 1.0, 0.0)
v5 = m.vertex(1.5, 1.0, 0.0)
v6 = m.vertex(2.5, 1.0, 0.0)

t0 = m.triangle(v0, v1, v4)   # CCW, +Z — the component_init seed
t1 = m.triangle(v1, v4, v5)   # CW (!), -Z — the defect triangle reachable from t0
# t1 normal: (v4-v1)×(v5-v1) = (-0.5,1,0)×(0.5,1,0) = (0,0,-0.5-0.5) = (0,0,-1) → -Z ✓
t2 = m.triangle(v1, v2, v5)   # CCW, +Z — reachable from t1

# t0 and t1 share edge v1-v4; their normals are antiparallel (the defect).
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)

# Shared edge between t0 (seed) and t1 (defect).
m.assert_edge_shared(v1, v4, 2)

# Shared edge between t1 and t2 (DFS propagation).
m.assert_edge_shared(v1, v5, 2)
