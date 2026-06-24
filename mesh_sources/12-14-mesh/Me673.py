"""Me673 — checkAndRepair::mergeCoincidentEdges branch 4: EDGE_DUPLICATION_BOUNDARY.

MeshFix `checkAndRepair::mergeCoincidentEdges` Branch 4 (*EDGE_DUPLICATION_BOUNDARY*) @ line 292:
  'pe = e->v1->getEdge(e->v2);' followed by vtxEdgeCompare — after v1 and v2
  have been remapped to their canonical representatives, the algorithm looks up
  whether a boundary edge connecting the same (canonical) vertex pair already
  exists in the half-edge structure. If getEdge finds an existing edge pe
  (pe != NULL) and both e and pe are boundary edges, then two boundary edges
  have identical endpoint pairs — a duplicate-boundary-edge condition. Branch 4
  fires when this duplicate is detected.

Defect pattern: two triangle patches that share a seam consisting of two
  distinct boundary edges connecting the same pair of canonical vertices.
  Patch A contributes boundary edge (c0, c1) and patch B contributes boundary
  edge (c0', c1') where c0'==c0 and c1'==c1 (exact coordinate coincidence).
  After vertex canonicalization, both edges map to the same canonical pair,
  triggering the vtxEdgeCompare branch.

Geometry:
  c0 = (0, 0, 0)  — shared seam left vertex (canonical)
  c1 = (1, 0, 0)  — shared seam right vertex (canonical)
  c2 = (0.5, 1, 0) — patch A apex
  d0 = (0, 0, 0)  — coincident with c0 (stitchable)
  d1 = (1, 0, 0)  — coincident with c1 (stitchable)
  d2 = (0.5,-1, 0) — patch B apex (below the seam)
  t0 = (c0, c1, c2) — patch A: seam edge (c0,c1) is boundary n=1
  t1 = (d0, d1, d2) — patch B: seam edge (d0,d1) is boundary n=1
  After vertex canonicalization (d0->c0, d1->c1), both boundary edges become
  (c0,c1) → getEdge(c0,c1) finds pe != NULL → Branch 4 fires; vtxEdgeCompare
  selects the canonical edge and merges triangle references.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me673",
    title="mergeCoincidentEdges EDGE_DUPLICATION_BOUNDARY: two boundary edges (c0,c1) and (d0,d1) at identical coordinates form a stitchable seam; vtxEdgeCompare selects canonical (Branch 4)",
    defect_class="near_coincident_vertex",
)

c0 = m.vertex(0.0,  0.0, 0.0)   # 0 — seam left, canonical
c1 = m.vertex(1.0,  0.0, 0.0)   # 1 — seam right, canonical
c2 = m.vertex(0.5,  1.0, 0.0)   # 2 — patch A apex (above seam)
d0 = m.vertex(0.0,  0.0, 0.0)   # 3 — coincident with c0
d1 = m.vertex(1.0,  0.0, 0.0)   # 4 — coincident with c1
d2 = m.vertex(0.5, -1.0, 0.0)   # 5 — patch B apex (below seam)

t0 = m.triangle(c0, c1, c2)     # 0 — patch A (seam on bottom)
t1 = m.triangle(d0, d1, d2)     # 1 — patch B (seam on top, mirrored)

# Boundary edges for patch A.
m.assert_edge_shared(c0, c1, 1)   # seam edge — will find duplicate in patch B
m.assert_edge_shared(c1, c2, 1)
m.assert_edge_shared(c0, c2, 1)

# Boundary edges for patch B.
m.assert_edge_shared(d0, d1, 1)   # duplicate seam — same canonical pair after merge
m.assert_edge_shared(d1, d2, 1)
m.assert_edge_shared(d0, d2, 1)

# Coincident vertex pairs across the seam.
m.assert_vertex_pair_distance_lt(c0, d0, 1e-9)
m.assert_vertex_pair_no_shared_triangle(c0, d0)
m.assert_vertex_pair_distance_lt(c1, d1, 1e-9)
m.assert_vertex_pair_no_shared_triangle(c1, d1)

# Both seam edges are spatially coincident (same endpoint coordinates).
m.assert_edge_pair_coincident((c0, c1), (d0, d1), eps=1e-9)

# Euler: V=6, E=6, F=2, chi=2 (two separate open disks pre-merge).
m.assert_euler_characteristic(6, 6, 2, 2)
