"""Me346 — init_info_preservation_flag: clone_info=true copies per-triangle info pointers.

MeshFix `Basic_TMesh.init` Branch 7 (*INFO_PRESERVATION_FLAG*) @ line 217:
  'if (clone_info) { ... nt->info = t->info; ... }' — when the caller passes
  clone_info=true, the init method copies the void* info pointer from each source
  triangle to its clone. This path is exercised when the caller wants to preserve
  external metadata (e.g. face IDs or property pointers) across the mesh copy.
  If the source mesh has degenerate triangles, their info pointers (often NULL
  in the defect case) are also copied verbatim.

Defect pattern: a mesh with a mix of 2 valid triangles and 1 near-coincident-vertex
  degenerate triangle. The near-coincident pair (v1, v2) is sub-tolerance close —
  a healer might tag the degenerate triangle with a special info pointer before calling
  init with clone_info=true. The clone inherits the broken pointer.

Geometry: v0=(0,0,0), v1=(1,0,0), v2=(1+1e-8,0,0) — near-coincident with v1.
  v3=(0.5,1,0).
  t0=(v0,v1,v3) — valid; t1=(v0,v1,v2) — near-degenerate via coincident v1/v2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me346",
             title="init_info_preservation_flag: near-coincident vertex pair forces clone_info to copy degenerate triangle info pointer",
             defect_class="near_coincident_vertex")

v0 = m.vertex(0.0,       0.0, 0.0)
v1 = m.vertex(1.0,       0.0, 0.0)
v2 = m.vertex(1.0 + 1e-8, 0.0, 0.0)   # sub-tolerance offset from v1
v3 = m.vertex(0.5,       1.0, 0.0)

t0 = m.triangle(v0, v1, v3)   # 0: valid triangle
t1 = m.triangle(v0, v1, v2)   # 1: near-degenerate — v1 and v2 are sub-epsilon coincident

# Near-coincident vertex pair confirmation.
m.assert_vertex_pair_distance_lt(v1, v2, 1e-6)

# The near-degenerate triangle has effectively zero area.
m.assert_triangle_area_lt(1, 1e-9)

# Edge incidence.
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
