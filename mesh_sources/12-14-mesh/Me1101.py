"""Me1101 — CreateTriangleFromVertices_over_constrained_e2: e2 already has 2 triangles (Branch 2).

MeshFix `Basic_TMesh.CreateTriangleFromVertices` Branch 2 (*OVER_CONSTRAINED_EDGE*) @ line 264:
  `if (IS_BIT(e2, 5)) { ... }`
  When edge e2 (the second edge of the target triangle) already has two incident
  triangles, both t1/t2 slots are occupied. Branch 2 detects IS_BIT(e2,5) and
  duplicates e2 so the new triangle gets a topologically independent edge copy.

In CreateTriangleFromVertices, edges e1, e2, e3 are the three bounding edges of
the triangle to be created. The checks are ordered: e1 passes (not over-constrained)
but e2 fails because IS_BIT(e2,5) is set — its two slots are already taken.

Defect carrier: edge (v1,v2) is shared by three triangles. The two base triangles
t0=(v0,v1,v2) and t1=(v3,v1,v2) fill both slots of e2. A third triangle
t2=(v4,v1,v2) attempts to use the same edge as e2, triggering IS_BIT(e2,5).
Edge e1=(v4,v0) for the seed triangle is distinct and not over-constrained;
only e2 fires Branch 2.

Geometry (star fan around edge (v1,v2)):
  v0=(0,0,0)    — apex of seed triangle (e1 endpoint)
  v1=(1,0,0)    — shared edge tail
  v2=(1,1,0)    — shared edge head
  v3=(2,0,0)    — apex of base triangle t0 (right side)
  v4=(0,1,0)    — apex of base triangle t1 (left side)
  v5=(1,0.5,1)  — out-of-plane apex for third sharer t2
  t0=(v3,v1,v2), t1=(v4,v1,v2) — fill both slots of edge (v1,v2)
  t2=(v5,v1,v2) — third triangle; e2=(v1,v2) is over-constrained → Branch 2
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1101",
    title="CreateTriangleFromVertices_over_constrained_e2: e2=(v1,v2) already has 2 triangles; IS_BIT(e2,5) triggers edge duplication (Branch 2)",
    defect_class="non_manifold_edge",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left apex (boundary)
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — shared edge tail
v2 = m.vertex(1.0, 1.0, 0.0)   # 2 — shared edge head
v3 = m.vertex(2.0, 0.0, 0.0)   # 3 — right apex of t0
v4 = m.vertex(0.0, 1.0, 0.0)   # 4 — top-left apex of t1
v5 = m.vertex(1.0, 0.5, 1.0)   # 5 — out-of-plane apex of t2

# Two base triangles fill both slots of edge (v1,v2).
t0 = m.triangle(v3, v1, v2)   # 0 — occupies e2->t1
t1 = m.triangle(v4, v1, v2)   # 1 — occupies e2->t2

# Third triangle: e2=(v1,v2) is over-constrained — IS_BIT(e2,5) fires → Branch 2.
t2 = m.triangle(v5, v1, v2)   # 2 — third sharer of (v1,v2)

# Edge (v1,v2) is incident on 3 triangles — the over-constrained defect for e2.
m.assert_edge_shared(v1, v2, 3)

# All other edges are boundary (each on exactly 1 triangle).
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v1, v4, 1)
m.assert_edge_shared(v2, v4, 1)
m.assert_edge_shared(v1, v5, 1)
m.assert_edge_shared(v2, v5, 1)
