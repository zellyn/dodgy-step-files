"""Me870 — selectIntersectingTriangles selected-vs-full-mesh: isSelection flag
chooses selT/selV subset rather than processing the entire mesh (Branch 1).

MeshFix `Basic_TMesh.selectIntersectingTriangles` Branch 1 (*Selected-vs-full-mesh*) @ line 149:
  'if (isSelection) { selT = ...; selV = ...; }' — when the caller passes
  isSelection=true, spatial partitioning is seeded from only the pre-selected
  triangle subset (selT / selV) rather than from the complete triangle list.
  Branch 1 fires whenever isSelection is non-zero, causing the spatial-partition
  cell builder to iterate over the selection rather than the whole mesh.

This fixture presents a mesh where a strict subset of two triangles is pre-
selected as potential intersectors. The selected pair (t0, t1) genuinely
self-intersects, while the remaining triangles (t2, t3) are clean and lie
far from the selected pair. The isSelection path limits the spatial scan to
the {t0, t1} subset, avoiding an unnecessary full-mesh pass.

Defect pattern: 'isSelection', 'selT', 'selV' — partial pre-selection of
  intersecting triangle subset causes spatial partitioner to restrict its
  cell-building to those two triangles.

Geometry:
  Selected pair (t0, t1) — two crossing triangles:
    t0 lies in the XY plane: v0=(0,0,0), v1=(2,1,0), v2=(2,-1,0)
    t1 lies in the XZ plane: v0=(0,0,0), v3=(2,0,1), v4=(2,0,-1)
    They cross along the positive X half-axis (shared apex v0).
  Unselected pair (t2, t3) — clean triangles far away at X=10:
    t2: v5=(10,0,0), v6=(12,1,0), v7=(12,-1,0)
    t3: v8=(10,3,0), v9=(12,4,0), v10=(12,2,0)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me870",
    title="selectIntersectingTriangles selected-vs-full-mesh: isSelection restricts spatial scan to pre-selected intersecting pair (Branch 1)",
    defect_class="self_intersection_face_pair",
)

# Selected pair: two crossing triangles sharing apex at origin.
v0 = m.vertex(0.0,  0.0,  0.0)   # 0 — shared apex
v1 = m.vertex(2.0,  1.0,  0.0)   # 1 — XY-plane slab
v2 = m.vertex(2.0, -1.0,  0.0)   # 2 — XY-plane slab
v3 = m.vertex(2.0,  0.0,  1.0)   # 3 — XZ-plane slab
v4 = m.vertex(2.0,  0.0, -1.0)   # 4 — XZ-plane slab

t0 = m.triangle(v0, v1, v2)      # 0: XY-plane — pre-selected
t1 = m.triangle(v0, v3, v4)      # 1: XZ-plane — pre-selected; crosses t0

# Unselected clean triangles far from the selection (X=10).
v5  = m.vertex(10.0,  0.0, 0.0)  # 5
v6  = m.vertex(12.0,  1.0, 0.0)  # 6
v7  = m.vertex(12.0, -1.0, 0.0)  # 7
v8  = m.vertex(10.0,  3.0, 0.0)  # 8
v9  = m.vertex(12.0,  4.0, 0.0)  # 9
v10 = m.vertex(12.0,  2.0, 0.0)  # 10

t2 = m.triangle(v5, v6, v7)      # 2: unselected — no SI
t3 = m.triangle(v8, v9, v10)     # 3: unselected — no SI

# The pre-selected pair (t0, t1) crosses along the X-axis.
m.assert_triangles_self_intersect(t0, t1)

# The unselected triangles are coplanar in the XY-plane and spatially separated.
m.assert_triangles_do_not_intersect(t2, t3)
