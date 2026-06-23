"""Me265 — range_with_face_set_marked_faces_topological_disk: complex removal via face marking.

Catalog claim: CGAL PMP.remove_degenerate_edges.range_with_face_set Branch 6 @ line 1678
(*non_link_condition_marked_faces*): when simple edge collapse is not possible (link
condition violated), the algorithm marks a set of faces around the degenerate edge
for multi-face removal. It validates that the marked region forms a topological disk
(add_center_vertex path), then stars the hole to complete the removal.

The marked_faces strategy: collect faces around the failing edge, validate them as a
topological disk (simply connected region with a single boundary loop), then remove
the region and fill with a star subdivision.

Geometric signature: a diamond mesh where the near-degenerate edge (v0,v1) fails the
link condition, but the surrounding marked faces form a topological disk. The marked
region consists of the two triangles incident on (v0,v1) plus their outer neighbours,
all forming a simply connected disk.

  Degenerate edge: v0≈v1 (near-zero length)
  Shared neighbours v2 (above) and v3 (below) are also in the marked region.
  The marked faces {t0,t1,t2,t3} form a closed disk (all 4 triangles around v0,v1).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me265",
             title="range_with_face_set marked_faces_topological_disk: non-link-condition edge removed via face-marking + disk validation",
             defect_class="degenerate_edge")

# Near-coincident vertex pair — link condition violated (shared neighbours v2 and v3).
v0 = m.vertex(0.0,   0.0, 0.0)
v1 = m.vertex(1e-10, 0.0, 0.0)

v2 = m.vertex(0.0,  1.0, 0.0)    # above: in both link rings → link condition violated
v3 = m.vertex(0.0, -1.0, 0.0)    # below: in both link rings → link condition violated

# Outer diamond vertices.
v4 = m.vertex(-1.0,  0.0, 0.0)   # left outer
v5 = m.vertex(1.0,   0.0, 0.0)   # right outer

# Six triangles forming a diamond; the inner 2 share degenerate edge (v0,v1);
# the outer 4 extend to form the topological disk region.
t0 = m.triangle(v0, v1, v2)   # 0: inner upper — degenerate edge
t1 = m.triangle(v1, v0, v3)   # 1: inner lower — degenerate edge
t2 = m.triangle(v4, v0, v2)   # 2: outer upper-left
t3 = m.triangle(v2, v1, v5)   # 3: outer upper-right
t4 = m.triangle(v4, v3, v0)   # 4: outer lower-left
t5 = m.triangle(v3, v5, v1)   # 5: outer lower-right

# The degenerate edge (v0,v1) is interior: shared by t0 and t1.
m.assert_edge_shared(v0, v1, 2)

# v0 and v1 are nearly coincident.
m.assert_vertex_pair_distance_lt(v0, v1, 1e-9)

# The two inner triangles sharing the degenerate edge have near-zero area.
m.assert_triangle_area_lt(t0, 1e-7)
m.assert_triangle_area_lt(t1, 1e-7)

# All 6 triangles form a single connected component (the topological disk).
# The whole mesh has Euler characteristic: V=6, E=11 (count manually):
# Edges from triangles: (0,1),(1,2),(0,2),(0,3),(1,3),(0,4),(2,4),(1,5),(2,5),(0,5)?
# Let's count: t0:(0,1),(1,2),(0,2); t1:(0,1),(0,3),(1,3); t2:(0,2),(0,4),(2,4);
#              t3:(1,2),(1,5),(2,5); t4:(0,3),(0,4),(3,4)? wait t4=(4,3,0)
# t4=(4,3,0): edges (3,4),(0,3),(0,4); t5=(3,5,1): edges (3,5),(1,5),(1,3)
# Unique edges: (0,1),(0,2),(1,2),(0,3),(1,3),(0,4),(2,4),(1,5),(2,5),(3,4),(3,5)...
# = 11 edges. V=6, E=11, F=6, chi = 6-11+6 = 1 (open disk, genus 0 with boundary).
m.assert_euler_characteristic(v=6, e=11, f=6, chi=1)
