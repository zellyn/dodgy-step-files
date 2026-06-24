"""Me490 — sanitize_candidates empty_input: candidate_hedges_with_id is empty; return immediately (Branch 1).

CGAL PMP `PMP.internal.sanitize_candidates` Branch 1 (*empty_input*) @ line 77:
  'if(candidate_hedges_with_id.empty()) return true;'
  — when no candidate groups were produced for the boundary cycle
  (because all coincident vertices in the cycle share a triangle and are
  therefore filtered out before sanitize_candidates is called), the
  candidate list is empty and the function returns true immediately.

Defect pattern: two triangles sharing an interior edge, where the two
  coincident boundary vertices ARE neighbours (share the interior edge),
  so detect_identical_mergeable_vertices never promotes them to
  candidate_hedges_with_id. Because the list stays empty,
  sanitize_candidates is entered with candidate_hedges_with_id.empty()
  == true → Branch 1 fires.

Geometry:
  e0=(0,0,0), e1=(1,0,0) [apex], e2=(1,0,0) [coincident with e1 coords,
  but e1 is the shared interior vertex], e3=(0,1,0).

  Actually, to guarantee empty_input we need coincident vertices that
  share a triangle (making them ineligible as candidate pairs).
  Use a single boundary cycle with exactly two coincident vertices that
  are connected by an interior edge — they share two triangles, so the
  pair never enters candidate_hedges_with_id → empty on entry to
  sanitize_candidates.

  v0=(0,0,0), v1=(2,0,0) [coincident with v3], v2=(1,2,0),
  v3=(2,0,0) [coincident with v1 but shares triangle t0 and t1].
  Wait: if v1 and v3 share a triangle they cannot form a candidate pair.

  Simpler: one boundary cycle, two coincident vertices that share a
  triangle directly.
  v0=(0,0,0), v1=(1,0,0), v2=(1,0,0) [=v1 coords].
  t0=(v0,v1,v2): all three in one triangle. But (v1,v2) would be an
  interior edge only if in 2 triangles — here it is only in t0, so it
  is a boundary edge. Mesh has degenerate zero-area triangle.

  Better: three vertices, two coincident, sharing the edge between them:
  v0=(0,0,0), v1=(1,0,0), v2=(1,0,0) [coincident with v1], v3=(0,1,0).
  t0=(v0,v1,v3): interior edge (v0,v3) shared with t1.
  t1=(v0,v2,v3): coincident v1,v2 share triangle? No — v1 is in t0 only,
  v2 is in t1 only. They are NOT in a shared triangle.

  To get empty_input: use a boundary cycle whose single "coincident" pair
  consists of the same vertex referenced twice (topology has no distinct
  index). Instead, produce a mesh with a single group that is removed by
  the dedup step inside detect_identical_mergeable_vertices before
  sanitize_candidates is ever reached, keeping candidate_hedges_with_id
  empty. The simplest realisation: only ONE coincident vertex pair, but
  that pair shares a common triangle — they are adjacent in the mesh
  and hence filtered. Under those conditions candidate_hedges_with_id
  remains empty; sanitize_candidates is called with an empty list.

  Design: three triangles; coincident vertices v1 and v3 both at (1,0,0);
  v1 and v3 share triangle t1=(v1,v2,v3).
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(1,0,0) [=v1 coords], v4=(1.5,1,0).
  t0=(v0,v1,v2): shares (v1,v2) with... need t1 to share (v1,v2).
  t1=(v1,v3,v2) so edges (v1,v2) shared with t0, (v3,v2) is new, (v1,v3) is new.
  t2=(v0,v2,v4): uses v4. Edges: (v0,v2) shared, (v2,v4),(v0,v4).
  (v0,v2) would be in t0 and t2 → n=2 interior.
  Interior: (v0,v2), (v1,v2). Boundary: (v0,v1),(v1,v3),(v3,v2),(v2,v4),(v0,v4).
  v1 and v3 share triangle t1 → they form a shared-triangle pair (NOT a candidate).
  Euler: V=5, E=7, F=3, chi=1.

Index ranges of coincident groups:
  Only one group before filter: {v1, v3} at (1,0,0).
  After the shared-triangle filter inside detect_identical_mergeable_vertices
  removes this pair, candidate_hedges_with_id is empty.
  sanitize_candidates(empty) → Branch 1: return true immediately.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me490",
    title="sanitize_candidates empty_input: coincident v1==v3 share triangle t1; candidate_hedges_with_id empty on entry; return immediately (Branch 1)",
    defect_class="near_coincident_vertex",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left base
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — coincident with v3; in t0 and t1
v2 = m.vertex(0.5, 1.0, 0.0)  # 2 — upper left
v3 = m.vertex(1.0, 0.0, 0.0)  # 3 — coincident with v1; in t1 (shares triangle with v1)
v4 = m.vertex(1.5, 1.0, 0.0)  # 4 — upper right

# t0=(v0,v1,v2): left triangle.
# t1=(v1,v3,v2): middle triangle; v1 and v3 share this triangle → not a candidate pair.
# t2=(v0,v2,v4): right triangle.
t0 = m.triangle(v0, v1, v2)  # 0: left
t1 = m.triangle(v1, v3, v2)  # 1: middle — v1 and v3 share this face
t2 = m.triangle(v0, v2, v4)  # 2: right

# Interior shared edges (n=2).
m.assert_edge_shared(v0, v2, 2)  # t0 and t2
m.assert_edge_shared(v1, v2, 2)  # t0 and t1

# Boundary edges (n=1).
m.assert_edge_shared(v0, v1, 1)  # t0 bottom-left
m.assert_edge_shared(v1, v3, 1)  # t1 bottom
m.assert_edge_shared(v2, v3, 1)  # t1 right
m.assert_edge_shared(v2, v4, 1)  # t2 upper-right
m.assert_edge_shared(v0, v4, 1)  # t2 bottom-right

# v1 and v3 are coincident but share triangle t1 → filtered before sanitize_candidates.
m.assert_vertex_pair_distance_lt(v1, v3, 1e-9)

# Euler: V=5, E=7, F=3, chi=1 (open disk).
m.assert_euler_characteristic(5, 7, 3, 1)
