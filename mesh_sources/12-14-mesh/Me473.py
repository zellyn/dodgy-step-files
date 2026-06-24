"""Me473 — remove_a_border_edge region_not_topological_disk: marked faces form non-disk topology (Branch 4).

CGAL PMP `PMP.remove_a_border_edge.with_sets` Branch 4 (*region_not_topological_disk*) @ line 1296:
  '!is_selection_a_topological_disk(marked_faces, tmesh)' → true; skip removal, return null_vertex.

After marking the faces incident to the candidate region, the algorithm checks
whether the marked faces form a topological disk (Euler characteristic = 1 for an
open surface with one boundary component). If they do not — e.g. the region is
annular (has a hole through it) — the check fails and the algorithm aborts.

An annular ring topology has Euler characteristic 0 (one surface with two boundary
components), so is_selection_a_topological_disk returns false → Branch 4 fires.

Geometry: 6-triangle annular ring (cylinder band).
  The ring consists of two rows of triangles wrapped to form an annulus.
  Outer boundary: v0,v1,v2,v3 (square outer loop)
  Inner boundary: v4,v5,v6,v7 (square inner loop, in the center)
  Triangles: t0=(v0,v1,v5), t1=(v0,v5,v4) — front face pair
             t2=(v1,v2,v6), t3=(v1,v6,v5) — right face pair
             t4=(v2,v3,v7), t5=(v2,v7,v6) — back face pair
             t6=(v3,v0,v4), t7=(v3,v4,v7) — left face pair

  Simpler 4-triangle annular ring:
  outer: v0=(0,0,0), v1=(2,0,0), v2=(2,2,0), v3=(0,2,0)
  inner: v4=(0.5,0.5,0), v5=(1.5,0.5,0), v6=(1.5,1.5,0), v7=(0.5,1.5,0)
  8 triangles: 2 per side.

  Simplest annular ring: 6 triangles (uneven split).
  Use 4 quads each split into 2 triangles = 8 triangles total.
  V=8, E=16, F=8, chi = 8-16+8=0 → annulus (Euler=0, not a disk).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me473",
    title="remove_a_border_edge region_not_topological_disk: 8-triangle annular ring has chi=0; is_selection_a_topological_disk returns false (Branch 4)",
    defect_class="border_edge_region_not_topological_disk",
)

# Outer ring vertices (CCW).
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 2.0, 0.0)   # 2
v3 = m.vertex(0.0, 2.0, 0.0)   # 3

# Inner ring vertices (CW in XY plane so normals point upward with CCW outer).
v4 = m.vertex(0.5, 0.5, 0.0)   # 4
v5 = m.vertex(1.5, 0.5, 0.0)   # 5
v6 = m.vertex(1.5, 1.5, 0.0)   # 6
v7 = m.vertex(0.5, 1.5, 0.0)   # 7

# Bottom band: v0-v1 outer edge, v4-v5 inner edge.
t0 = m.triangle(v0, v1, v5)   # 0
t1 = m.triangle(v0, v5, v4)   # 1

# Right band: v1-v2 outer, v5-v6 inner.
t2 = m.triangle(v1, v2, v6)   # 2
t3 = m.triangle(v1, v6, v5)   # 3

# Top band: v2-v3 outer, v6-v7 inner.
t4 = m.triangle(v2, v3, v7)   # 4
t5 = m.triangle(v2, v7, v6)   # 5

# Left band: v3-v0 outer, v7-v4 inner.
t6 = m.triangle(v3, v0, v4)   # 6
t7 = m.triangle(v3, v4, v7)   # 7

# Outer boundary edges (n=1): the outer perimeter.
m.assert_edge_shared(v0, v1, 1)   # border edge (outer) — trigger edge
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v0, 1)

# Inner boundary edges (n=1): the inner hole perimeter.
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, v6, 1)
m.assert_edge_shared(v6, v7, 1)
m.assert_edge_shared(v7, v4, 1)

# Interior edges shared by 2 triangles each (each corner shared by adjacent triangles in same band,
# plus diagonal within each band).
m.assert_edge_shared(v0, v4, 2)   # left-band: shared by t1 and t6
m.assert_edge_shared(v0, v5, 2)   # bottom-band: shared by t0 and t1
m.assert_edge_shared(v1, v5, 2)   # bottom/right corner: shared by t0 and t3
m.assert_edge_shared(v1, v6, 2)   # right-band: shared by t2 and t3
m.assert_edge_shared(v2, v6, 2)   # right/top corner: shared by t2 and t5
m.assert_edge_shared(v2, v7, 2)   # top-band: shared by t4 and t5
m.assert_edge_shared(v3, v7, 2)   # top/left corner: shared by t4 and t7
m.assert_edge_shared(v3, v4, 2)   # left-band: shared by t6 and t7

# Euler characteristic: V=8, E=16, F=8, chi=0 → annular topology (NOT a disk).
# This is exactly what causes is_selection_a_topological_disk to return false → Branch 4.
m.assert_euler_characteristic(8, 16, 8, 0)
