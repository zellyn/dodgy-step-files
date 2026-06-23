"""Me353 — CreateTriangle_triangle_creation: newTriangle(e1,e2,e3) instantiates triangle object.

MeshFix `Basic_TMesh.CreateTriangle` Branch 4 (*triangle_creation*) @ line 375:
  `tt = newTriangle(e1, e2, e3);`
  After the three slot pointers at1/at2/at3 are resolved (Branches 1-3), the new
  triangle object `tt` is instantiated from the three edges. This is the core
  allocating step.

Defect carrier: a single new well-formed triangle with all three boundary edges
(the minimum geometry produced when newTriangle is called for the first and only
triangle in a mesh). The triangle is fully created: all three edges belong to it,
and all edges are boundary (n=1) since there is no adjacent mesh context.

Geometry:
  v0=(0,0,0), v1=(3,0,0), v2=(1.5,2,0) — equilateral-ish triangle
  t0=(v0,v1,v2) — the newly created triangle (newTriangle result)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me353",
    title="CreateTriangle_triangle_creation: tt=newTriangle(e1,e2,e3) allocates triangle object (Branch 4)",
    defect_class="create_triangle_new_object",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(3.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.5, 2.0, 0.0)   # 2

# The single freshly created triangle — newTriangle(e1,e2,e3) result.
t0 = m.triangle(v0, v1, v2)   # 0

# All three edges are boundary (n=1): tt has no neighbors yet.
m.assert_edge_shared(v0, v1, 1)   # e2 boundary
m.assert_edge_shared(v1, v2, 1)   # e1 boundary
m.assert_edge_shared(v0, v2, 1)   # e3 boundary

# The triangle is non-degenerate (positive area).
m.assert_triangle_area_lt(t0, 10.0)   # area = 3.0 < 10
