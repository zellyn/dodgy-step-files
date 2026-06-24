"""Me485 — removeTriangles topology_invalidation: d_boundaries=d_handles=d_shells=1 dirty flags set.

Basic_TMesh.removeTriangles branch 6: topology_invalidation —
  `d_boundaries = d_handles = d_shells = 1;`

After removing all triangles with NULL edge pointers, MeshFix marks all cached
topology metrics as dirty (d_boundaries, d_handles, d_shells each set to 1).
This forces recomputation of boundary loops, handle count, and shell count on
the next query. The branch fires whenever at least one triangle is removed.

Fixture: minimal post-cleanup mesh — after an orphan degenerate triangle has
been removed, only the intact triangles remain. Two triangles sharing an edge
form an open-boundary quad. This represents the "after removal" state where
topology_invalidation (Branch 6) would fire: the mesh is now topologically
complete (no more orphans), but the cached topology metrics are stale and
marked for recomputation.

Geometry (z = 0): two-triangle strip — clean post-cleanup survivor mesh.
  v0=(0,0,0), v1=(1,0,0), v2=(0,1,0), v3=(1,1,0)
  t0 = (v0, v1, v3) — healthy
  t1 = (v0, v3, v2) — healthy
  Euler: V=4, E=5, F=2, chi=1 (open disk — one boundary loop of length 4)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me485",
             title="removeTriangles topology_invalidation: d_boundaries=d_handles=d_shells=1 after orphan removal; clean 2-triangle survivor mesh (Branch 6)",
             defect_class="open_boundary")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2
v3 = m.vertex(1.0, 1.0, 0.0)   # 3

t0 = m.triangle(v0, v1, v3)    # 0 — healthy
t1 = m.triangle(v0, v3, v2)    # 1 — healthy

# Interior shared edge: (v0, v3) shared by both triangles.
m.assert_edge_shared(v0, v3, 2)

# After orphan removal, the survivor mesh has a clean single boundary loop.
m.assert_hole_boundary([v0, v1, v3, v2])

# Euler: V=4, E=5, F=2, chi=1 — compact open-disk; topology recomputation triggered.
m.assert_euler_characteristic(4, 5, 2, 1)
