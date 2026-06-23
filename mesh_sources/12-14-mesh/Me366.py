"""Me366 — remove_isolated_points_index_remapping: polygon vertex indices renumbered after point removal.

CGAL PMP `remove_isolated_points_in_polygon_soup` Branch 7 (*index_remapping*) @ line 471:
  'for(P_ID polygon_index=0; ...) { for(i=0; ...) { polygon[i] = id_remapping[polygon[i]]; } }' —
  after erasing the isolated tail, the function remaps every polygon's vertex indices
  through id_remapping[] so that indices still point to the correct (compacted) positions.

Defect pattern: a triangle (v0,v1,v2) with an isolated vertex v3 inserted *between*
  referenced vertices in the list. When the swap phase moves v3 to the tail, the
  referenced vertex that was swapped into position 3 now has a new index (3), but the
  original polygon that referenced it still holds the old index. The remap step fixes
  all polygon references. Here we place the isolated vertex at index 1 (middle) so
  that the remap is non-trivial: v1_orig (was at index 1) gets remapped to the new
  index after the compact.

Geometry: v0=(0,0,0), v_iso=(5,5,5) at index 1, v1=(1,0,0) at index 2, v2=(0.5,1,0)
  at index 3. Triangle references indices 0, 2, 3 (skipping the isolated vertex at 1).
  After removal and remap, the triangle will reference 0, 1, 2 in the compacted list.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me366",
             title="remove_isolated_points_index_remapping: isolated vertex at non-tail position forces non-trivial index remap",
             defect_class="isolated_vertex")

# v_iso is at index 1, inserted before the triangle vertices to force remap.
v0   = m.vertex(0.0, 0.0, 0.0)   # index 0 — referenced
v_iso = m.vertex(5.0, 5.0, 5.0)  # index 1 — isolated (orphan)
v1   = m.vertex(1.0, 0.0, 0.0)   # index 2 — referenced
v2   = m.vertex(0.5, 1.0, 0.0)   # index 3 — referenced

# Triangle uses indices 0, 2, 3 — v_iso (index 1) is not referenced.
m.triangle(v0, v1, v2)

# Isolated vertex at index 1.
m.assert_isolated_vertex(v_iso)

# Triangle edges (open mesh).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
