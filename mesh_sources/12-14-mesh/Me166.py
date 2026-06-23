"""Me166 — stitch_edge_replacement: candidate edge e1 is replaced by stitch edge in triangle t.

MeshFix `Edge.stitch` Branch 7 (*STITCH_EDGE_REPLACEMENT*) @ line 387:
  't->replaceEdge(e1, this)'
  After finding candidate edge e1 and its triangle t, the stitch operation
  replaces e1 with the current stitch edge ('this') inside t. This topologically
  joins the two boundary chains: the triangle formerly connected via e1 is now
  connected via the stitch edge. Branch 7 is the core merge action.

Defect pattern: two separate open patches with a coincident boundary seam.
After stitching, triangle t (which was on Patch B using e1) will use the stitch
edge from Patch A instead. The fixture shows pre-stitch state: two patches with
a boundary gap where replaceEdge is about to be called.

Geometry: minimal two-patch seam — one triangle per patch, fully coincident boundary.
  Patch A: t0=(v0,v1,v2), boundary edge (v0,v1) — the stitch edge ('this')
  Patch B: t1=(v3,v4,v5), boundary edge (v3,v4) — the candidate e1

After replaceEdge: t1 uses (v0,v1) instead of (v3,v4). The two patches are joined.
This fixture captures the pre-stitch state where both boundary edges still exist.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me166",
             title="stitch_edge_replacement: candidate edge e1 replaced by stitch edge in triangle t via replaceEdge",
             defect_class="stitch_edge_replacement")

# Patch A — stitch edge is (v0,v1)
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

# Patch B — candidate edge (v3,v4) will be replaced by (v0,v1)
v3 = m.vertex(0.0, 0.0, 0.0)   # 3 — coincident to v0
v4 = m.vertex(1.0, 0.0, 0.0)   # 4 — coincident to v1
v5 = m.vertex(0.5, -1.0, 0.0)  # 5 — below (opposite side of seam)

t0 = m.triangle(v0, v1, v2)    # 0 — Patch A
t1 = m.triangle(v3, v4, v5)    # 1 — Patch B; e1=(v3,v4) will be replaced

# Both boundary edges are incident on exactly one triangle.
m.assert_edge_shared(v0, v1, 1)  # stitch edge ('this')
m.assert_edge_shared(v3, v4, 1)  # candidate e1 to be replaced

# Near-coincident pairs: seam to be joined
m.assert_vertex_pair_distance_lt(v0, v3, 1e-9)
m.assert_vertex_pair_distance_lt(v1, v4, 1e-9)

# Other boundary edges
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v4, v5, 1)
