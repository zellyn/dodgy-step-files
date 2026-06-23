"""Me236 — topTriangle_steepest_edge_filter: edge incident on hv passes hasVertex+nonzero test.

MeshFix `Basic_TMesh.topTriangle` Branch 7 (*steepest_edge_filter*) @ line 1719:
  'e->hasVertex(hv) && e->length() != 0' — edge in elist is incident on the
  highest vertex AND has nonzero length; passes filter for slope computation.

After hv (highest vertex) is identified, topTriangle scans elist for edges that
(a) connect hv to some other vertex and (b) have nonzero length. Branch 7 is the
guard that lets an edge enter slope comparison. The fixture has multiple edges in
elist, but only those incident on hv pass Branch 7.

Geometry: three vertices with a clear highest vertex (v2 at z=3):
  v0=(0,0,0), v1=(2,0,0), v2=(1,0,3)
  t0=(v0,v1,v2) — single triangle; all three edges are in elist.

hv=v2 (z=3). elist = {(v0,v1), (v1,v2), (v0,v2)}.
  - (v0,v1): does NOT have v2 → Branch 7 fails for this edge.
  - (v1,v2): has v2, length=sqrt(1+9)≈3.16 ≠ 0 → Branch 7 passes.
  - (v0,v2): has v2, length=sqrt(1+9)≈3.16 ≠ 0 → Branch 7 passes.

Both (v1,v2) and (v0,v2) pass the filter; slope comparison in Branch 8 picks
the steepest. The base edge (v0,v1) is rejected by Branch 7 (does not touch hv).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me236",
             title="topTriangle_steepest_edge_filter: edges incident on hv=v2 pass hasVertex+nonzero filter",
             defect_class="topTriangle_steepest_edge_filter")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 0.0, 3.0)   # 2 — hv (z=3 highest)

t0 = m.triangle(v0, v1, v2)   # 0 — single triangle

# All three edges are boundary.
m.assert_edge_shared(v0, v1, 1)   # base edge — does NOT touch hv; fails Branch 7
m.assert_edge_shared(v1, v2, 1)   # passes Branch 7 (incident on hv=v2)
m.assert_edge_shared(v0, v2, 1)   # passes Branch 7 (incident on hv=v2)

# Hole boundary = triangle perimeter.
m.assert_hole_boundary([v0, v1, v2])

# v2 is strictly highest: z=3 >> z=0 for v0 and v1.
# The two candidate edges both have nonzero length (~3.16 each).
m.assert_vertex_pair_distance_lt(v0, v2, 4.0)
m.assert_vertex_pair_distance_lt(v1, v2, 4.0)
