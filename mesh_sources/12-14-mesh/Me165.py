"""Me165 — stitch_triangle_merger: get incident triangle of matched candidate edge.

MeshFix `Edge.stitch` Branch 6 (*STITCH_TRIANGLE_MERGER*) @ line 386:
  't = (e1->t1 != NULL) ? (e1->t1) : (e1->t2)'
  Once the candidate stitch edge e1 is found, stitch retrieves the one triangle
  incident on e1 (it must be a boundary edge, so exactly one slot is non-NULL).
  Branch 6 covers the t1-slot case: e1->t1 is non-NULL and selected as t.

Defect pattern: two open patches with coincident boundary. The candidate stitch
edge e1 has its incident triangle stored in the t1 slot. The fixture is a boundary
gap between two open patches (three triangles total: two on Patch A connected, one
on Patch B with coincident boundary edge whose triangle is in t1 slot).

Geometry: open L-strip with unstitched seam.
  Patch A: t0=(v0,v1,v2), t1=(v1,v3,v2) — connected interior
  Patch B: t2=(v4,v5,v6) — isolated triangle, boundary (v4,v5) coincident to (v1,v2)

The boundary edge (v4,v5) on Patch B has its incident triangle t2 in the t1 field.
After the walk finds e1=(v4,v5), Branch 6 selects e1->t1 (= t2) as the merge target.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me165",
             title="stitch_triangle_merger: candidate stitch edge e1 has incident triangle in t1 slot",
             defect_class="stitch_triangle_merger_t1")

# Patch A
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — shared interior apex
v3 = m.vertex(1.5, 1.0, 0.0)   # 3

# Patch B — boundary coincident to (v1,v2)
v4 = m.vertex(1.0, 0.0, 0.0)   # 4 — coincident to v1
v5 = m.vertex(0.5, 1.0, 0.0)   # 5 — coincident to v2
v6 = m.vertex(2.0, 0.5, 0.0)   # 6 — outer vertex of Patch B

t0 = m.triangle(v0, v1, v2)    # 0 — Patch A left
t1 = m.triangle(v1, v3, v2)    # 1 — Patch A right, shares (v1,v2) with t0
t2 = m.triangle(v4, v5, v6)    # 2 — Patch B; boundary (v4,v5) is stitch candidate

# (v1,v2) interior (Patch A); (v4,v5) boundary (Patch B candidate).
m.assert_edge_shared(v1, v2, 2)  # interior — stitch source
m.assert_edge_shared(v4, v5, 1)  # boundary candidate (t1 slot occupied)

# Near-coincident: unstitched seam
m.assert_vertex_pair_distance_lt(v1, v4, 1e-9)
m.assert_vertex_pair_distance_lt(v2, v5, 1e-9)

# Other boundary edges
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v4, v6, 1)
m.assert_edge_shared(v5, v6, 1)
