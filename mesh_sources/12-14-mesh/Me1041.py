"""Me1041 — stitch_borders non-border-edge-skip: interior edges skipped in border halfedge collection loop.

CGAL PMP `PMP.stitch_borders (internal dispatcher)` Branch 2 (*non-border-edge-skip*) @ line 440:
  'if (!is_border(h, mesh)) continue;'
  As the dispatcher iterates over all halfedges to collect border edges, it checks
  each halfedge for boundary status and skips non-border (interior) halfedges.
  Branch 2 fires for every interior halfedge that is skipped, confirming that only
  true boundary halfedges enter the candidate pool.

Defect pattern: a three-triangle fan sharing a central interior edge plus two
  additional interior edges, surrounded by an open boundary. The mesh has both
  interior halfedges (skipped by Branch 2) and boundary halfedges (collected for
  stitching). The presence of interior edges exercises the continue branch.

Geometry:
  v0=(0,0,0) — hub vertex
  v1=(1,0,0), v2=(0,1,0), v3=(-1,0,0) — outer vertices
  t0=(v0,v1,v2) — interior edge (v0,v1) and (v0,v2) are shared
  t1=(v0,v2,v3) — interior edge (v0,v2)
  t2=(v0,v3,v1) — closes the fan; interior edge (v0,v3) and (v0,v1)
  Wait — this would be a closed surface. Use an open fan instead:
  t0=(v0,v1,v2), t1=(v0,v2,v3) sharing (v0,v2); open boundary.
  Interior: (v0,v2) n=2. Boundary: (v0,v1),(v1,v2),(v2,v3),(v0,v3) n=1 each.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1041",
    title="stitch_borders non-border-edge-skip: is_border check skips interior halfedges; open fan mesh with mixed interior/boundary edges",
    defect_class="boundary_gap_thin",
)

# Open two-triangle fan with one interior edge
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — hub
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — outer
v2 = m.vertex(0.0, 1.0, 0.0)   # 2 — shared outer (on interior edge)
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3 — outer

t0 = m.triangle(v0, v1, v2)    # 0 — left triangle
t1 = m.triangle(v0, v2, v3)    # 1 — right triangle; shares (v0,v2) with t0

# Interior edge: (v0,v2) shared by t0 and t1 — is_border returns false → continue
m.assert_edge_shared(v0, v2, 2)

# Boundary edges — is_border returns true → collected for stitching
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Euler: V=4, E=5, F=2, chi=1 (open disk)
m.assert_euler_characteristic(4, 5, 2, 1)
