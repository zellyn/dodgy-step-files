"""Me1071 — filter_stitchable_pairs border-two-edge-exception: exactly two border halfedges on merged edge; stitching is manifold-safe (Branch 2).

CGAL PMP `PMP.filter_stitchable_pairs (manifold validator)` Branch 2 (*border-two-edge-exception*) @ line 723:
  'case 2: if(is_border_edge(it->second[0], mesh) && is_border_edge(it->second[1], mesh)) break;'
  — when the occurrence map shows exactly 2 halfedges for a candidate edge, the
  algorithm checks whether both are border halfedges. If both come from open boundary
  loops, the merge is manifold-safe (they form the two sides of the new interior edge)
  → Branch 2 fires and the pair is kept.

Defect pattern: two triangulated patches sharing exactly one coincident boundary
  edge pair. After the proposed vertex merge the candidate edge has exactly 2
  halfedges — one from each patch — both of which are border edges. This is the
  canonical stitch-borders success case: Branch 2 accepts the pair.

Geometry:
  Patch A: triangle p0=(0,0,0), p1=(1,0,0), p2=(0.5,1,0) — right edge (p1,p2) is
    the stitchable boundary.
  Patch B: triangle q0=(2,0,0), q1=(1,0,0), q2=(0.5,1,0) — left edge (q1,q2)
    is the stitchable boundary; q1≡p1, q2≡p2 geometrically.
  After merge p1≡q1 and p2≡q2: the merged edge (p1,p2) has exactly 2 halfedges
  (one from t0, one from t1), both border → Branch 2 fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1071",
    title="filter_stitchable_pairs border-two-edge-exception: two border halfedges on coincident boundary edge; both border → manifold-safe stitch accepted (Branch 2)",
    defect_class="near_coincident_vertex",
)

# Patch A: right edge (p1,p2) is the stitchable boundary.
p0 = m.vertex(0.0, 0.0, 0.0)   # 0
p1 = m.vertex(1.0, 0.0, 0.0)   # 1 — coincident with q1
p2 = m.vertex(0.5, 1.0, 0.0)   # 2 — coincident with q2
t0 = m.triangle(p0, p1, p2)    # 0: patch A

# Patch B: left edge (q1,q2) is the stitchable boundary; q1==p1, q2==p2.
q0 = m.vertex(2.0, 0.0, 0.0)   # 3
q1 = m.vertex(1.0, 0.0, 0.0)   # 4 — coincident with p1 at (1,0,0)
q2 = m.vertex(0.5, 1.0, 0.0)   # 5 — coincident with p2 at (0.5,1,0)
t1 = m.triangle(q0, q1, q2)    # 1: patch B (note: winding reversed vs A for joining)

# All six edges are boundary (n=1) — two patches not yet topologically connected.
m.assert_edge_shared(p0, p1, 1)   # patch A base
m.assert_edge_shared(p0, p2, 1)   # patch A left
m.assert_edge_shared(p1, p2, 1)   # patch A right — stitchable
m.assert_edge_shared(q0, q1, 1)   # patch B base
m.assert_edge_shared(q0, q2, 1)   # patch B right
m.assert_edge_shared(q1, q2, 1)   # patch B left — stitchable (coincident with p1,p2)

# Coincident vertex pairs targeted by filter_stitchable_pairs.
m.assert_vertex_pair_distance_lt(p1, q1, 1e-9)   # both at (1,0,0)
m.assert_vertex_pair_distance_lt(p2, q2, 1e-9)   # both at (0.5,1,0)
m.assert_vertex_pair_no_shared_triangle(p1, q1)
m.assert_vertex_pair_no_shared_triangle(p2, q2)

# Euler: V=6, E=6, F=2, chi=2 (two separate open disks).
m.assert_euler_characteristic(6, 6, 2, 2)
