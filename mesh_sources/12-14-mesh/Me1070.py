"""Me1070 — filter_stitchable_pairs edge-occurrence-limit: single halfedge per merged edge accepted (Branch 1).

CGAL PMP `PMP.filter_stitchable_pairs (manifold validator)` Branch 1 (*edge-occurrence-limit*) @ line 721:
  'case 1: /* single halfedge on this edge — manifold boundary, ok */'
  — after tentatively merging coincident boundary vertex pairs, the algorithm
  builds an occurrence map from each edge (canonical vertex pair) to the set of
  halfedges that would touch it. Branch 1 fires when an edge in the merged map
  has exactly one halfedge (i.e. the edge would remain a simple open boundary
  after stitching), confirming the pair is manifold-safe.

Defect pattern: two separate triangular patches whose shared boundary consists
  of exactly one coincident edge pair. The proposed stitch merges v1→a1 and
  v2→a2; the resulting interior edge (merged pair) appears exactly once in the
  occurrence map — Branch 1 fires for that edge slot. The remaining boundary
  edges each have a single occurrence as well, also exercising Branch 1.

Geometry:
  Patch A: triangle v0=(0,0,0), v1=(1,0,0), v2=(0,1,0) — three boundary edges.
  Patch B: triangle a0=(2,0,0), a1=(1,0,0), a2=(0,1,0) [=v1/v2 coords] — open.
  Coincident boundary edge between (v1,v2) and (a1,a2):
    v1 at (1,0,0) == a1; v2 at (0,1,0) == a2.
  After stitch: that edge becomes interior (count=2 for this specific merge-pair);
  the remaining boundary edges each have count=1 → Branch 1 fires for each.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1070",
    title="filter_stitchable_pairs edge-occurrence-limit: two-patch boundary with single coincident-edge pair; count=1 boundary slots confirm manifold safety (Branch 1)",
    defect_class="near_coincident_vertex",
)

# Patch A: three boundary edges.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — bottom-left corner
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — bottom-right; coincident with a1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2 — top-left; coincident with a2
t0 = m.triangle(v0, v1, v2)    # 0: patch A

# Patch B: three boundary edges; a1/a2 coincident with v1/v2.
a0 = m.vertex(2.0, 0.0, 0.0)   # 3 — isolated corner of patch B
a1 = m.vertex(1.0, 0.0, 0.0)   # 4 — coincident with v1 at (1,0,0)
a2 = m.vertex(0.0, 1.0, 0.0)   # 5 — coincident with v2 at (0,1,0)
t1 = m.triangle(a0, a1, a2)    # 1: patch B

# All edges are boundary (each triangle is isolated — 1 shared count each).
m.assert_edge_shared(v0, v1, 1)    # patch A bottom
m.assert_edge_shared(v0, v2, 1)    # patch A left
m.assert_edge_shared(v1, v2, 1)    # patch A hypotenuse (to-stitch side)
m.assert_edge_shared(a0, a1, 1)    # patch B bottom
m.assert_edge_shared(a0, a2, 1)    # patch B left
m.assert_edge_shared(a1, a2, 1)    # patch B hypotenuse (to-stitch side)

# Coincident vertex pairs that filter_stitchable_pairs must evaluate.
m.assert_vertex_pair_distance_lt(v1, a1, 1e-9)
m.assert_vertex_pair_distance_lt(v2, a2, 1e-9)
m.assert_vertex_pair_no_shared_triangle(v1, a1)
m.assert_vertex_pair_no_shared_triangle(v2, a2)

# Euler: V=6, E=6, F=2, chi=2 (two disconnected open disks).
m.assert_euler_characteristic(6, 6, 2, 2)
