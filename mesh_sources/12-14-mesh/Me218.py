"""Me218 — cutAndStitch_cleanup_unlinked: orphaned elements swept after pinch operations.

MeshFix `Basic_TMesh.cutAndStitch` Branch 9 (*CLEANUP_UNLINKED*) @ line 1023:
  'removeUnlinkedElements()'
  After pinch operations stitch boundary pairs, some vertices, edges, or
  triangles become orphaned (unlinked from the mesh topology). cutAndStitch
  calls removeUnlinkedElements() to sweep and free these dangling elements,
  leaving a clean manifold mesh.

Defect pattern: an isolated vertex not referenced by any triangle — the classic
post-merge orphan. After cutAndStitch stitches seam edges together, original
vertices at the seam may become unreferenced if their role was replaced by merged
vertices. removeUnlinkedElements() frees these.

Geometry: a single triangle plus a stray isolated vertex.
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0) — triangle vertices
  v3=(2,2,2) — isolated vertex (not referenced by any triangle)
  t0=(v0,v1,v2)

  v3 is the unlinked orphan that removeUnlinkedElements() must free.
  This mirrors the post-pinch state where the seam vertex is still in the
  vertex list but no longer connected to any triangle.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me218",
             title="cutAndStitch_cleanup_unlinked: isolated orphan vertex swept by removeUnlinkedElements()",
             defect_class="isolated_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(2.0, 2.0, 2.0)   # 3 — orphan; removeUnlinkedElements() target

t0 = m.triangle(v0, v1, v2)   # 0 — only triangle

# v3 is isolated — not referenced by any triangle.
m.assert_isolated_vertex(v3)

# Triangle boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
