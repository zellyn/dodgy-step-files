"""Me1072 — filter_stitchable_pairs multi-edge-vertex-disqualification: 3 coincident halfedges on merged edge; vertices added to unstitchable set (Branch 3).

CGAL PMP `PMP.filter_stitchable_pairs (manifold validator)` Branch 3 (*multi-edge-vertex-disqualification*) @ line 728:
  'default: /* 3 or more halfedges — non-manifold, disqualify all vertices */
   for(auto h : it->second) {
     unstitchable_vertices.insert(source(h, mesh));
     unstitchable_vertices.insert(target(h, mesh)); }'
  — when 3 or more halfedges would share the same edge after the proposed vertex
  merge, the result would be a non-manifold edge. All four vertices (source and
  target of each offending halfedge) are inserted into the unstitchable set →
  Branch 3 fires.

Defect pattern: three triangular patches with coincident boundary vertices on one
  edge, so that after tentative vertex merge the occurrence map shows 3 halfedges
  on that edge. Stitching would produce a non-manifold edge (fan of 3 faces).
  Branch 3 fires for the problematic edge and all 6 incident vertices are marked
  unstitchable.

Geometry:
  Patch A: triangle u0=(0,0,0), u1=(1,0,0), u2=(0,1,0) — edge (u1,u2) is boundary.
  Patch B: triangle b0=(2,0,0), b1=(1,0,0), b2=(0,1,0) — edge (b1,b2) is boundary.
  Patch C: triangle c0=(-1,0,0), c1=(1,0,0), c2=(0,1,0) — edge (c1,c2) is boundary.
  All three edges (u1,u2), (b1,b2), (c1,c2) are coincident:
    u1=b1=c1 at (1,0,0) and u2=b2=c2 at (0,1,0).
  After tentative merge, the edge (u1,u2) accumulates 3 halfedges → default
  case fires → Branch 3 disqualifies all incident vertices.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1072",
    title="filter_stitchable_pairs multi-edge-vertex-disqualification: 3 coincident boundary halfedges on same merged edge; default case marks all vertices unstitchable (Branch 3)",
    defect_class="near_coincident_vertex",
)

# Patch A: isolated triangle; edge (u1,u2) is one of three coincident boundary edges.
u0 = m.vertex(0.0, 0.0, 0.0)   # 0 — patch A corner
u1 = m.vertex(1.0, 0.0, 0.0)   # 1 — coincident seam vertex; matches b1 and c1
u2 = m.vertex(0.0, 1.0, 0.0)   # 2 — coincident seam vertex; matches b2 and c2
t0 = m.triangle(u0, u1, u2)    # 0: patch A

# Patch B: isolated triangle; b1==u1, b2==u2 geometrically.
b0 = m.vertex(2.0, 0.0, 0.0)   # 3 — patch B corner
b1 = m.vertex(1.0, 0.0, 0.0)   # 4 — at (1,0,0); coincident with u1 and c1
b2 = m.vertex(0.0, 1.0, 0.0)   # 5 — at (0,1,0); coincident with u2 and c2
t1 = m.triangle(b0, b1, b2)    # 1: patch B

# Patch C: isolated triangle; c1==u1, c2==u2 geometrically.
c0 = m.vertex(-1.0, 0.0, 0.0)  # 6 — patch C corner (negative-x side)
c1 = m.vertex(1.0, 0.0, 0.0)   # 7 — at (1,0,0); third coincident copy
c2 = m.vertex(0.0, 1.0, 0.0)   # 8 — at (0,1,0); third coincident copy
t2 = m.triangle(c0, c1, c2)    # 2: patch C

# All nine edges are boundary (n=1) — three disconnected patches.
m.assert_edge_shared(u0, u1, 1)    # patch A bottom
m.assert_edge_shared(u0, u2, 1)    # patch A left
m.assert_edge_shared(u1, u2, 1)    # patch A hypotenuse — one of three coincident
m.assert_edge_shared(b0, b1, 1)    # patch B bottom
m.assert_edge_shared(b0, b2, 1)    # patch B left
m.assert_edge_shared(b1, b2, 1)    # patch B hypotenuse — one of three coincident
m.assert_edge_shared(c0, c1, 1)    # patch C bottom-right
m.assert_edge_shared(c0, c2, 1)    # patch C left
m.assert_edge_shared(c1, c2, 1)    # patch C hypotenuse — one of three coincident

# Three-way coincident seam: u1/b1/c1 all at (1,0,0); u2/b2/c2 all at (0,1,0).
m.assert_vertex_pair_distance_lt(u1, b1, 1e-9)
m.assert_vertex_pair_distance_lt(u1, c1, 1e-9)
m.assert_vertex_pair_distance_lt(u2, b2, 1e-9)
m.assert_vertex_pair_distance_lt(u2, c2, 1e-9)
m.assert_vertex_pair_no_shared_triangle(u1, b1)
m.assert_vertex_pair_no_shared_triangle(u1, c1)
m.assert_vertex_pair_no_shared_triangle(u2, b2)
m.assert_vertex_pair_no_shared_triangle(u2, c2)

# Euler: V=9, E=9, F=3, chi=3 (three disconnected open disks).
m.assert_euler_characteristic(9, 9, 3, 3)
