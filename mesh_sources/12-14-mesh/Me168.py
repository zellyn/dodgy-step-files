"""Me168 — stitch_orphan_edge: candidate edge e1 nulled out after stitch (orphaned).

MeshFix `Edge.stitch` Branch 9 (*STITCH_ORPHAN_EDGE*) @ line 389:
  'e1->v1 = e1->v2 = NULL'
  After the triangle's edge reference is updated (replaceEdge) and vertex anchors
  are patched, the now-redundant candidate edge e1 is de-linked by nulling its
  vertex pointers. This marks e1 as an orphan — an unlinked edge that can be freed
  in the next cleanup sweep. Branch 9 covers this orphan-edge creation step.

Defect pattern: two patches with a coincident boundary seam. After stitching, the
candidate edge e1 becomes an orphan (v1=NULL, v2=NULL). The fixture captures the
pre-stitch state: e1 is a boundary edge incident on exactly one triangle, about
to be orphaned when stitch nulls its vertex pointers.

Geometry: two separate triangles, both with a boundary edge along the X-axis.
  Patch A: t0=(v0,v1,v2), stitch edge (v0,v1).
  Patch B: t1=(v3,v4,v5), candidate e1=(v3,v4), geometrically coincident to (v0,v1).

Post-stitch: e1->v1 = e1->v2 = NULL; (v3,v4) edge is an unlinked orphan.
The oracle asserts pre-stitch boundary state — both edges incident on 1 triangle.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me168",
             title="stitch_orphan_edge: candidate e1 nulled (v1=v2=NULL) after boundary stitch to become orphaned edge",
             defect_class="stitch_orphan_edge")

# Patch A
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

# Patch B — e1=(v3,v4) coincident to (v0,v1), will be orphaned
v3 = m.vertex(0.0, 0.0, 0.0)   # 3 — coincident to v0
v4 = m.vertex(1.0, 0.0, 0.0)   # 4 — coincident to v1
v5 = m.vertex(0.5, -1.0, 0.0)  # 5

t0 = m.triangle(v0, v1, v2)    # 0 — Patch A
t1 = m.triangle(v3, v4, v5)    # 1 — Patch B; e1=(v3,v4) will be orphaned

# Pre-stitch: both seam edges are boundary edges (incident on 1 triangle each).
m.assert_edge_shared(v0, v1, 1)  # stitch edge ('this')
m.assert_edge_shared(v3, v4, 1)  # candidate e1 (pre-orphan state)

# Coincident vertex pairs confirm the geometry of the seam.
m.assert_vertex_pair_distance_lt(v0, v3, 1e-9)
m.assert_vertex_pair_distance_lt(v1, v4, 1e-9)

# Other boundary edges
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v4, v5, 1)
