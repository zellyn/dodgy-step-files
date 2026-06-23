"""Me169 — stitch_interior_conversion: stitch edge transitions from boundary to interior.

MeshFix `Edge.stitch` Branch 10 (*STITCH_INTERIOR_CONVERSION*) @ line 390:
  'replaceTriangle(NULL, t)'
  The final step of a successful stitch: the stitch edge ('this') previously had
  one NULL triangle slot (it was a boundary edge). Now that the candidate triangle
  t has been wired to use 'this' instead of e1, the stitch edge gets a second
  incident triangle. replaceTriangle(NULL, t) fills the NULL slot with t, making
  the edge interior (two incident triangles). Branch 10 is the boundary-to-interior
  transition.

Defect pattern: two open patches whose boundary seam is about to be closed. The
stitch edge starts with one incident triangle (boundary) and ends with two
(interior). The fixture shows the pre-stitch state: two patches with a coincident
seam where the stitch edge will transition from boundary to interior.

Geometry: two mirrored triangles sharing a coincident boundary along the X-axis.
  Patch A: t0=(v0,v1,v2) above the X-axis; stitch edge (v0,v1) is boundary (n=1)
  Patch B: t1=(v3,v4,v5) below the X-axis; candidate (v3,v4) coincident to (v0,v1)

Post-stitch: (v0,v1) becomes interior — incident on both t0 and (the relocated) t1.
The edge transitions from n=1 to n=2 via replaceTriangle(NULL, t1).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me169",
             title="stitch_interior_conversion: stitch edge transitions from boundary (n=1) to interior (n=2) via replaceTriangle(NULL,t)",
             defect_class="stitch_interior_conversion")

# Patch A — above X-axis
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — above seam

# Patch B — below X-axis (mirror triangle)
v3 = m.vertex(0.0, 0.0, 0.0)   # 3 — coincident to v0
v4 = m.vertex(1.0, 0.0, 0.0)   # 4 — coincident to v1
v5 = m.vertex(0.5, -1.0, 0.0)  # 5 — below seam (mirror of v2)

t0 = m.triangle(v0, v1, v2)    # 0 — Patch A
t1 = m.triangle(v3, v4, v5)    # 1 — Patch B; candidate e1=(v3,v4)

# Pre-stitch: stitch edge is boundary (n=1); post-stitch it becomes interior (n=2).
m.assert_edge_shared(v0, v1, 1)  # pre-stitch: boundary; will become n=2 after replaceTriangle
m.assert_edge_shared(v3, v4, 1)  # candidate e1 (will be orphaned after stitch)

# Near-coincident seam vertices
m.assert_vertex_pair_distance_lt(v0, v3, 1e-9)
m.assert_vertex_pair_distance_lt(v1, v4, 1e-9)

# Remaining boundary edges (will become the full boundary post-stitch)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v4, v5, 1)
