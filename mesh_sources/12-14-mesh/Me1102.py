"""Me1102 — CreateTriangleFromVertices_over_constrained_e3: e3 already has 2 triangles (Branch 3).

MeshFix `Basic_TMesh.CreateTriangleFromVertices` Branch 3 (*OVER_CONSTRAINED_EDGE*) @ line 265:
  `if (IS_BIT(e3, 5)) { ... }`
  When edge e3 (the third bounding edge of the target triangle) already has two
  incident triangles, Branch 3 detects IS_BIT(e3,5) and duplicates e3 so the new
  triangle receives a topologically independent edge object.

In CreateTriangleFromVertices the checks proceed in order: e1 passes, e2 passes,
but e3 fires IS_BIT check because both its t1/t2 slots are occupied by existing
triangles. The defect is specifically on the third edge of the seed triangle.

Defect carrier: edge (v2,v0) is shared by three triangles. The two base triangles
t0=(v0,v1,v2) and t1=(v2,v0,v3) fill both slots of e3. A third triangle
t2=(v2,v0,v4) attempts to use the same edge as e3, triggering IS_BIT(e3,5).
Edges e1 and e2 of the seed triangle are distinct and not over-constrained;
only e3 fires Branch 3.

Geometry (star fan around edge (v0,v2)):
  v0=(0,0,0)    — shared edge tail
  v1=(1,0,0)    — base apex (t0 only)
  v2=(0,1,0)    — shared edge head
  v3=(1,1,0)    — base apex (t1 only)
  v4=(-1,0.5,1) — out-of-plane apex for third sharer t2
  t0=(v0,v1,v2), t1=(v2,v0,v3) — fill both slots of edge (v0,v2)
  t2=(v2,v0,v4) — third triangle; e3=(v2,v0)=(v0,v2) is over-constrained → Branch 3
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1102",
    title="CreateTriangleFromVertices_over_constrained_e3: e3=(v0,v2) already has 2 triangles; IS_BIT(e3,5) triggers edge duplication (Branch 3)",
    defect_class="non_manifold_edge",
)

v0 = m.vertex( 0.0, 0.0, 0.0)   # 0 — shared edge tail
v1 = m.vertex( 1.0, 0.0, 0.0)   # 1 — base apex of t0
v2 = m.vertex( 0.0, 1.0, 0.0)   # 2 — shared edge head
v3 = m.vertex( 1.0, 1.0, 0.0)   # 3 — base apex of t1
v4 = m.vertex(-1.0, 0.5, 1.0)   # 4 — out-of-plane apex of t2

# Two base triangles fill both slots of edge (v0,v2).
t0 = m.triangle(v0, v1, v2)   # 0 — occupies e3->t1 (uses (v0,v2) as e3)
t1 = m.triangle(v2, v0, v3)   # 1 — occupies e3->t2

# Third triangle: e3=(v2,v0) is over-constrained — IS_BIT(e3,5) fires → Branch 3.
t2 = m.triangle(v2, v0, v4)   # 2 — third sharer of (v0,v2)

# Edge (v0,v2) is incident on 3 triangles — the over-constrained defect for e3.
m.assert_edge_shared(v0, v2, 3)

# All other edges are boundary (each on exactly 1 triangle).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v2, v4, 1)
