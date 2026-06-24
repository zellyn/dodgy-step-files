"""Me1046 — stitch_borders single-pass-manifold-filtering: global mode processes all border edges in one pass with manifold filtering.

CGAL PMP `PMP.stitch_borders (internal dispatcher)` Branch 7 (*single-pass-manifold-filtering*) @ line 492:
  'else { manifold_halfedge_pairs(pairs, mesh); ... }'
  When per_cc=false (global mode, single connected component), the dispatcher
  collects all border halfedges in a single global pass, then calls
  manifold_halfedge_pairs once to filter the complete candidate list. Branch 7 fires
  in non-per_cc mode when the mesh is a single connected component.

Defect pattern: a single connected open mesh strip with a stitchable seam. Both
  patches are connected via shared vertices (not just coincident), making the mesh
  a single connected component. With per_cc=false, the dispatcher takes the else
  branch and performs global manifold filtering on all collected halfedge pairs in
  one pass.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(1.5,1,0)
    t0=(v0,v1,v2), t1=(v1,v3,v2) — interior edge (v1,v2); open boundary strip
  v4=(1,0,0)[=v1], v5=(0.5,1,0)[=v2], v6=(0,0,0)[=v0] — coincident seam
  v7=(0.5,-1,0) — additional vertex; bottom triangle shares v0 and v1
    t2=(v0,v4,v7) — connected to Patch A via shared vertex v0;
                     seam edge (v0,v4) coincident with (v0,v1)
  Actually: ensure single CC by chaining triangles without a real seam gap.
  Use a flat L-shaped open strip (all connected, single CC) with one boundary
  edge coincident to another boundary edge (thin boundary gap / duplicate boundary).

  Minimal single-CC mesh with coincident boundary:
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(0,0,0)[=v0], v4=(2,0,0)[=v1]
  t0=(v0,v1,v2) — base
  t1=(v2,v3,v0) — shares (v0,v2) with t0; v3 coincident with v0
  Hmm — this gets complicated. Use the cleanest approach:
  Single CC with an open seam: two triangles sharing a central edge, open boundary.
  Coincident boundary vertices show the seam. Single CC so global mode fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1046",
    title="stitch_borders single-pass-manifold-filtering: global mode (per_cc=false) single CC; manifold_halfedge_pairs called once for all collected pairs",
    defect_class="boundary_gap_thin",
)

# Single connected component — open strip
v0 = m.vertex(0.0, 0.0, 0.0)    # 0
v1 = m.vertex(1.0, 0.0, 0.0)    # 1
v2 = m.vertex(0.5, 1.0, 0.0)    # 2
v3 = m.vertex(1.5, 0.0, 0.0)    # 3

# Coincident seam vertices (potential stitch targets)
v4 = m.vertex(0.5, 1.0, 0.0)    # 4 — coincident with v2
v5 = m.vertex(1.5, 0.0, 0.0)    # 5 — coincident with v3

t0 = m.triangle(v0, v1, v2)     # 0
t1 = m.triangle(v1, v3, v2)     # 1 — shares (v1,v2) with t0; single CC

# Coincident patch attached to Patch A via shared vertex v1
t2 = m.triangle(v1, v4, v5)     # 2 — connected via v1; seam (v4,v5) ~ (v2,v3)

# Interior edges
m.assert_edge_shared(v1, v2, 2)  # t0 and t1 share this

# All 3 meshes form a single connected component (t2 shares v1 with t0,t1)
# Seam: v2/v4 coincident, v3/v5 coincident — boundary edges to potentially stitch
m.assert_edge_shared(v2, v3, 1)  # Patch A boundary edge (part of seam)
m.assert_edge_shared(v4, v5, 1)  # Patch B boundary edge coincident with (v2,v3)

m.assert_vertex_pair_distance_lt(v2, v4, 1e-9)
m.assert_vertex_pair_distance_lt(v3, v5, 1e-9)
m.assert_vertex_pair_no_shared_triangle(v2, v4)
m.assert_vertex_pair_no_shared_triangle(v3, v5)

# Other boundary edges
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v1, v4, 1)
m.assert_edge_shared(v1, v5, 1)

# Single CC: t2 is reachable from t0 (via v1)
# Euler: V=6, E=8, F=3, chi=1 (single open disk)
m.assert_euler_characteristic(6, 8, 3, 1)
