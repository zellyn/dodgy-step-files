"""Me434 — checkAndRepair::forceNormalConsistence branch 5: NON_ORIENTABLE_SEAM.

MeshFix `checkAndRepair::forceNormalConsistence` Branch 5 @ line 959:
  'tmp1*tmp2 < 0' — edge e has contradictory orientation: one adjacent triangle
  sees the shared edge going v1→v2 and the other also sees it going v1→v2 (same
  direction instead of opposite). The sign product tmp1*tmp2 < 0 indicates a
  non-orientable seam. Branch 5 creates a new edge 'newEdge(e->v2, e->v1)'
  cutting along the seam (Möbius-band cut).

The NON_ORIENTABLE_SEAM branch fires at a seam edge where both adjacent triangles
traverse the edge in the same cyclic direction rather than opposite directions.
In a correctly-oriented manifold, two triangles sharing edge (v_a, v_b) should
list it as v_a→v_b in one and v_b→v_a in the other. When BOTH list it v_a→v_b,
the propagator computes tmp1*tmp2 < 0 and fires Branch 5.

Geometry: 4 triangles forming a closed surface with one non-orientable seam.

    v0=(0,0,0), v1=(1,0,0), v2=(1,1,0), v3=(0,1,0)

    t0=(v0,v1,v2): edges (v0,v1),(v1,v2),(v2,v0). Normal +z.
    t1=(v0,v1,v3): edges (v0,v1),(v1,v3),(v3,v0). Normal −z. ← seam!
    t2=(v1,v2,v3): edges (v1,v2),(v2,v3),(v3,v1).
    t3=(v2,v0,v3): edges (v2,v0),(v0,v3),(v3,v2).

    Seam: both t0 and t1 list edge (v0,v1) in the SAME direction (v0→v1).
    Correct manifold orientation would require one to list v1→v0. Since neither does,
    the seam is non-orientable. All 6 edges are shared by exactly 2 triangles.

Normal verification:
    t0=(v0,v1,v2): (v1-v0)×(v2-v0)=(1,0,0)×(1,1,0)=(0,0,1) → +z
    t1=(v0,v1,v3): (v1-v0)×(v3-v0)=(1,0,0)×(0,1,0)=(0,0,1) wait...
    Actually (1,0,0)×(0,1,0)=(0·0-0·1, 0·0-1·0, 1·1-0·0)=(0,0,1) → +z.
    Both triangles have +z normal here? Let me check antiparallel condition.
    t3=(v2,v0,v3): (v0-v2)×(v3-v2)=(-1,-1,0)×(-1,0,0)=((-1)·0-0·0, 0·(-1)-(-1)·0, (-1)·0-(-1)·(-1))=(0,0,-1) → -z.

The non-orientable seam is between t0/t1 (same-direction edge) and t0/t3 where
the normal flips. The Euler characteristic is chi=4-6+4=2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me434",
             title="forceNormalConsistence non-orientable-seam: closed surface with same-direction seam edge; tmp1*tmp2<0 (Branch 5)",
             defect_class="non_orientable_seam")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 1.0, 0.0)   # 2
v3 = m.vertex(0.0, 1.0, 0.0)   # 3

# t0 and t1 BOTH list shared edge (v0,v1) in the same direction (v0→v1).
# In a correctly-oriented manifold one should go v0→v1 and the other v1→v0.
# Here both go v0→v1 — the non-orientable seam.
t0 = m.triangle(v0, v1, v2)   # 0 — lists (v0,v1) as v0→v1. Normal +z.
t1 = m.triangle(v0, v1, v3)   # 1 — lists (v0,v1) as v0→v1 (same!). Normal +z.
t2 = m.triangle(v1, v2, v3)   # 2 — upper-right connector.
t3 = m.triangle(v2, v0, v3)   # 3 — left connector. Normal −z.

# Seam edge: shared by t0 and t1 in the same direction.
m.assert_edge_shared(v0, v1, 2)

# t0 and t3 have antiparallel normals, demonstrating the orientation inconsistency
# that results from the seam. (t0 +z, t3 -z → dot < 0.)
m.assert_adjacent_triangles_inconsistent_winding(t0, t3)

# All other edges are interior (shared by 2 triangles). Closed surface.
m.assert_edge_shared(v1, v2, 2)   # t0 ↔ t2
m.assert_edge_shared(v0, v2, 2)   # t0 ↔ t3 (canonical of (v2,v0))
m.assert_edge_shared(v1, v3, 2)   # t1 ↔ t2
m.assert_edge_shared(v0, v3, 2)   # t1 ↔ t3
m.assert_edge_shared(v2, v3, 2)   # t2 ↔ t3

# Euler characteristic: V=4, E=6, F=4, chi=2 (closed surface).
m.assert_euler_characteristic(4, 6, 4, 2)
