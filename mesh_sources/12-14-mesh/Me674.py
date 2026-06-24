"""Me674 — checkAndRepair::mergeCoincidentEdges branch 5: REDUNDANT_EDGE_REMOVAL.

MeshFix `checkAndRepair::mergeCoincidentEdges` Branch 5 (*REDUNDANT_EDGE_REMOVAL*) @ line 295:
  'if (e->info != e)' — after all vertex and edge merges have been performed,
  a second pass scans every edge looking for edges whose info pointer no longer
  points to themselves (i.e. they were marked as duplicates during Branch 4
  merging, and their info was redirected to the canonical edge). Branch 5 fires
  for each such redundant edge. The triangle(s) referencing it are redirected to
  the canonical edge via replaceEdge, then the duplicate edge is nulled out.

Defect pattern: an open two-patch mesh where the stitching seam has already
  been processed and the duplicate boundary edge has had its info pointer
  redirected (e->info == pe, the canonical edge). The second pass detects
  e->info != e and replaces the triangle reference. This state arises after
  Branch 4 runs — the canonical edge keeps info==self; the duplicate gets
  info=canonical.

  To expose this branch in a fixture we construct two patches whose seam
  vertices are exactly coincident (so vertex merge + edge merge fires), plus
  a third "witness" triangle adjacent to the seam on one side that provides
  the replaceEdge triangle-reference redirect.

Geometry:
  e0 = (0, 0, 0)  — seam left vertex, canonical
  e1 = (1, 0, 0)  — seam right vertex, canonical
  e2 = (0.5, 1, 0) — patch A apex
  f0 = (0, 0, 0)  — coincident with e0 (stitchable)
  f1 = (1, 0, 0)  — coincident with e1 (stitchable)
  f2 = (0.5,-1, 0) — patch B apex
  g2 = (1.5, 0.5, 0) — patch A second triangle apex
  t0 = (e0, e1, e2) — patch A first triangle; seam edge (e0,e1) → n=1
  t1 = (f0, f1, f2) — patch B triangle; seam edge (f0,f1) → n=1 (duplicate)
  t2 = (e1, g2, e2) — patch A second triangle; shares edge (e1,e2) with t0 → n=2
  After merge: f's seam edge info → e's seam edge (canonical); t1 reference
  is redirected via replaceEdge → Branch 5 fires during the info-redirect scan.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me674",
    title="mergeCoincidentEdges REDUNDANT_EDGE_REMOVAL: duplicate seam edge (f0,f1) has info redirected to canonical (e0,e1); replaceEdge redirects triangle reference (Branch 5)",
    defect_class="near_coincident_vertex",
)

e0 = m.vertex(0.0,  0.0, 0.0)   # 0 — seam left, canonical
e1 = m.vertex(1.0,  0.0, 0.0)   # 1 — seam right, canonical
e2 = m.vertex(0.5,  1.0, 0.0)   # 2 — patch A apex
f0 = m.vertex(0.0,  0.0, 0.0)   # 3 — coincident with e0
f1 = m.vertex(1.0,  0.0, 0.0)   # 4 — coincident with e1
f2 = m.vertex(0.5, -1.0, 0.0)   # 5 — patch B apex
g2 = m.vertex(1.5,  0.5, 0.0)   # 6 — patch A second triangle apex

t0 = m.triangle(e0, e1, e2)     # 0 — patch A main triangle
t1 = m.triangle(f0, f1, f2)     # 1 — patch B triangle (duplicate seam)
t2 = m.triangle(e1, g2, e2)     # 2 — patch A second triangle (shares edge with t0)

# Interior edge (e1,e2) shared by t0 and t2.
m.assert_edge_shared(e1, e2, 2)

# Seam edges: both are boundary edges (n=1) before merge.
m.assert_edge_shared(e0, e1, 1)   # canonical seam edge
m.assert_edge_shared(f0, f1, 1)   # duplicate — will get info=canonical; Branch 5 fires

# Other boundary edges.
m.assert_edge_shared(e0, e2, 1)
m.assert_edge_shared(f1, f2, 1)
m.assert_edge_shared(f0, f2, 1)
m.assert_edge_shared(e1, g2, 1)
m.assert_edge_shared(e2, g2, 1)

# Coincident vertex pairs across the seam.
m.assert_vertex_pair_distance_lt(e0, f0, 1e-9)
m.assert_vertex_pair_no_shared_triangle(e0, f0)
m.assert_vertex_pair_distance_lt(e1, f1, 1e-9)
m.assert_vertex_pair_no_shared_triangle(e1, f1)

# The two seam edges are spatially coincident — after vertex merge both map
# to canonical pair (e0,e1); the duplicate's info is redirected → Branch 5.
m.assert_edge_pair_coincident((e0, e1), (f0, f1), eps=1e-9)

# Euler: V=7, E=8, F=3, chi=2 (open disk A with 2 triangles + separate open disk B).
# V=7: e0,e1,e2,f0,f1,f2,g2
# E=8: (e0,e1),(e1,e2),(e0,e2),(f0,f1),(f1,f2),(f0,f2),(e1,g2),(e2,g2)
# chi = 7 - 8 + 3 = 2
m.assert_euler_characteristic(7, 8, 3, 2)
