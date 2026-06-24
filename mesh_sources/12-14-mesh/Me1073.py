"""Me1073 — filter_stitchable_pairs vertex-pair-safety-check: candidate halfedge pair excluded because one vertex is in unstitchable_vertices (Branch 4).

CGAL PMP `PMP.filter_stitchable_pairs (manifold validator)` Branch 4 (*vertex-pair-safety-check*) @ line 739:
  'for(auto& p : halfedge_pairs) {
     if(unstitchable_vertices.count(source(p.first, mesh)) ||
        unstitchable_vertices.count(target(p.first, mesh)) ||
        unstitchable_vertices.count(source(p.second, mesh)) ||
        unstitchable_vertices.count(target(p.second, mesh))) {
       /* skip this pair */ continue; }
     stitchable_pairs.push_back(p); }'
  — after Branch 3 populates unstitchable_vertices, all remaining candidate
  halfedge pairs are checked: if any of the four endpoint vertices of the pair
  appears in the unstitchable set, the pair is silently skipped → Branch 4 fires.

Defect pattern: four triangular patches in two groups.
  Group 1 (contaminating): three patches sharing a coincident triple edge (as in
  Me1072) — their seam vertices (s1/s2) are marked unstitchable by Branch 3.
  Group 2 (victim): two additional patches sharing a coincident boundary edge that
  is otherwise manifold-safe (count=2, both border). However, one endpoint of that
  edge is geometrically coincident with s1 — so vertex-pair-safety-check finds
  it in unstitchable_vertices and drops the pair → Branch 4 fires.

Geometry:
  Patches A/B/C (contaminating triple — triggers Branch 3):
    A: e0=(0,0,0), e1=(1,0,0), e2=(0,1,0)
    B: f0=(2,0,0), f1=(1,0,0), f2=(0,1,0) [f1==e1, f2==e2]
    C: g0=(-1,0,0), g1=(1,0,0), g2=(0,1,0) [g1==e1, g2==e2]
  Patches D/E (victim pair — would be stitchable but blocked):
    D: h0=(3,0,0), h1=(1,0,0), h2=(1,2,0) [h1==e1 → in unstitchable_vertices]
    E: k0=(4,0,0), k1=(1,0,0), k2=(1,2,0) [k1==e1 → in unstitchable_vertices]
  Edge (h1,h2)/(k1,k2) is coincident and would have count=2 (both border) — BUT
  h1 is in unstitchable_vertices (from the triple-edge contamination) → Branch 4
  excludes this pair even though it would otherwise be a valid stitch.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1073",
    title="filter_stitchable_pairs vertex-pair-safety-check: contaminating triple-edge marks e1/e2 unstitchable (Branch 3); victim pair (h1,h2)/(k1,k2) excluded because h1 in unstitchable_vertices (Branch 4)",
    defect_class="near_coincident_vertex",
)

# --- Contaminating group (Patches A, B, C) ---
# Three patches share coincident seam at e1=(1,0,0), e2=(0,1,0).
# Branch 3 will mark e1 and e2 (and their copies) as unstitchable.
e0 = m.vertex(0.0, 0.0, 0.0)   # 0
e1 = m.vertex(1.0, 0.0, 0.0)   # 1 — seam; will be marked unstitchable
e2 = m.vertex(0.0, 1.0, 0.0)   # 2 — seam; will be marked unstitchable
t0 = m.triangle(e0, e1, e2)    # 0: patch A

f0 = m.vertex(2.0, 0.0, 0.0)   # 3
f1 = m.vertex(1.0, 0.0, 0.0)   # 4 — coincident with e1
f2 = m.vertex(0.0, 1.0, 0.0)   # 5 — coincident with e2
t1 = m.triangle(f0, f1, f2)    # 1: patch B

g0 = m.vertex(-1.0, 0.0, 0.0)  # 6
g1 = m.vertex(1.0, 0.0, 0.0)   # 7 — coincident with e1 (third copy)
g2 = m.vertex(0.0, 1.0, 0.0)   # 8 — coincident with e2 (third copy)
t2 = m.triangle(g0, g1, g2)    # 2: patch C

# --- Victim group (Patches D, E) ---
# Would be a valid stitch (count=2, both border), but h1/k1 coincide with e1
# → already in unstitchable_vertices → Branch 4 excludes this pair.
h0 = m.vertex(3.0, 0.0, 0.0)   # 9
h1 = m.vertex(1.0, 0.0, 0.0)   # 10 — at (1,0,0), coincident with e1 (unstitchable)
h2 = m.vertex(1.0, 2.0, 0.0)   # 11 — top point of patch D
t3 = m.triangle(h0, h1, h2)    # 3: patch D

k0 = m.vertex(4.0, 0.0, 0.0)   # 12
k1 = m.vertex(1.0, 0.0, 0.0)   # 13 — at (1,0,0), coincident with e1 (unstitchable)
k2 = m.vertex(1.0, 2.0, 0.0)   # 14 — at (1,2,0), coincident with h2
t4 = m.triangle(k0, k1, k2)    # 4: patch E

# All edges are boundary (n=1) — five disconnected patches.
m.assert_edge_shared(e0, e1, 1)
m.assert_edge_shared(e0, e2, 1)
m.assert_edge_shared(e1, e2, 1)
m.assert_edge_shared(f0, f1, 1)
m.assert_edge_shared(f0, f2, 1)
m.assert_edge_shared(f1, f2, 1)
m.assert_edge_shared(g0, g1, 1)
m.assert_edge_shared(g0, g2, 1)
m.assert_edge_shared(g1, g2, 1)
m.assert_edge_shared(h0, h1, 1)
m.assert_edge_shared(h0, h2, 1)
m.assert_edge_shared(h1, h2, 1)
m.assert_edge_shared(k0, k1, 1)
m.assert_edge_shared(k0, k2, 1)
m.assert_edge_shared(k1, k2, 1)

# Contaminating triple seam: e1/f1/g1 at (1,0,0); e2/f2/g2 at (0,1,0).
m.assert_vertex_pair_distance_lt(e1, f1, 1e-9)
m.assert_vertex_pair_distance_lt(e1, g1, 1e-9)
m.assert_vertex_pair_distance_lt(e2, f2, 1e-9)
m.assert_vertex_pair_distance_lt(e2, g2, 1e-9)
m.assert_vertex_pair_no_shared_triangle(e1, f1)
m.assert_vertex_pair_no_shared_triangle(e1, g1)
m.assert_vertex_pair_no_shared_triangle(e2, f2)
m.assert_vertex_pair_no_shared_triangle(e2, g2)

# Victim pair: h1/k1 at (1,0,0), h2/k2 at (1,2,0).
# These would form a valid count=2 stitch, but h1 is contaminated by Branch 3.
m.assert_vertex_pair_distance_lt(h1, k1, 1e-9)
m.assert_vertex_pair_distance_lt(h2, k2, 1e-9)
m.assert_vertex_pair_no_shared_triangle(h1, k1)
m.assert_vertex_pair_no_shared_triangle(h2, k2)

# h1 is also coincident with the contaminating seam (e1).
m.assert_vertex_pair_distance_lt(e1, h1, 1e-9)
m.assert_vertex_pair_no_shared_triangle(e1, h1)

# Euler: V=15, E=15, F=5, chi=5 (five disconnected open disks).
m.assert_euler_characteristic(15, 15, 5, 5)
