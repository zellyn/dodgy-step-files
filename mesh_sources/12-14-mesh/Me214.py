"""Me214 — cutAndStitch_sort_singular_edges: boundary edges sorted for coincident grouping.

MeshFix `Basic_TMesh.cutAndStitch` Branch 5 (*SORT_SINGULAR_EDGES*) @ line 1006:
  'singular_edges.sort(&lexEdgeCompare)'
  After collecting all singular boundary edges, cutAndStitch sorts them
  lexicographically by coordinate so that coincident or near-coincident pairs
  end up adjacent in the list for grouping in Branch 6.

Defect pattern: a mesh with two separate boundary edge pairs whose vertices are
at coincident positions — they need to be sorted together for stitching. The
geometry represents two boundary patches with matching (but unconnected) edges
at the seam, as would result from an earlier cut operation.

Geometry: two patches sharing the same physical edge position but as disconnected
boundary edges.
  Patch A: v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0); t0=(v0,v1,v2)
  Patch B: v3=(0,0,0), v4=(1,0,0), v5=(0.5,-1,0); t1=(v3,v5,v4)
  v0==v3 and v1==v4 in position (near-coincident pairs).
  Edge (v0,v1) on t0 and edge (v3,v4) on t1 are coincident boundary edges
  that lexEdgeCompare would sort together.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me214",
             title="cutAndStitch_sort_singular_edges: coincident boundary edges sorted by lexEdgeCompare for grouping",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0, 0.0, 0.0)    # 0 — patch A left
v1 = m.vertex(1.0, 0.0, 0.0)    # 1 — patch A right
v2 = m.vertex(0.5, 1.0, 0.0)    # 2 — patch A apex

v3 = m.vertex(0.0, 0.0, 0.0)    # 3 — patch B left (coincident with v0)
v4 = m.vertex(1.0, 0.0, 0.0)    # 4 — patch B right (coincident with v1)
v5 = m.vertex(0.5, -1.0, 0.0)   # 5 — patch B apex

t0 = m.triangle(v0, v1, v2)    # 0 — patch A
t1 = m.triangle(v3, v5, v4)    # 1 — patch B (CW to face down)

# The seam edges are each on exactly one triangle (boundary).
m.assert_edge_shared(v0, v1, 1)   # patch A seam edge
m.assert_edge_shared(v3, v4, 1)   # patch B seam edge (coincident with A's)

# Near-coincident vertex pairs at the seam.
m.assert_vertex_pair_distance_lt(v0, v3, 1e-9)
m.assert_vertex_pair_distance_lt(v1, v4, 1e-9)

# Other boundary edges.
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v4, v5, 1)
