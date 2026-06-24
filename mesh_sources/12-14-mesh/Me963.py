"""Me963 — CreateUnorientedTriangle_unoriented_creation: newTriangle(e1,e2,e3) without orientation check.

MeshFix `Basic_TMesh.CreateUnorientedTriangle` Branch 4 (*unoriented_triangle_creation*) @ line 403:
  `tt = newTriangle(e1, e2, e3);`
  After slot pointers at1/at2/at3 are resolved (Branches 1-3), the new triangle
  object `tt` is instantiated via newTriangle(e1,e2,e3). Unlike CreateTriangle,
  no winding/orientation validation precedes this call — the triangle is created
  regardless of winding order.

Key distinction: CreateUnorientedTriangle is used when orientation consistency is
not required (e.g. filling degenerate holes where winding is unknown). The three
bounding edges are all boundary edges of the input mesh before creation.

Defect carrier: a mesh with three open boundary edges forming an isolated triangular
gap. All three edges have exactly one free slot (n=1) before the fill. After
CreateUnorientedTriangle the fill triangle tf occupies the open slots and each
edge becomes interior (n=2) — or the new triangle is the only triangle in the mesh
with all three edges as fresh boundaries.

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(1,1.732,0) — equilateral triangle
  tf=(v0,v1,v2) — the single newly created unoriented triangle
  All three edges are fresh boundaries (t1 used, n=1 each after creation).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me963",
    title="CreateUnorientedTriangle_unoriented_creation: newTriangle(e1,e2,e3) without orientation check (Branch 4)",
    defect_class="create_unoriented_triangle_new_object",
)

v0 = m.vertex(0.0, 0.0, 0.0)        # 0
v1 = m.vertex(2.0, 0.0, 0.0)        # 1
v2 = m.vertex(1.0, 1.732, 0.0)      # 2  (approx equilateral height)

# The single unoriented triangle — newTriangle(e1,e2,e3) result with no winding check.
tf = m.triangle(v0, v1, v2)   # 0

# All three edges are boundary (n=1): tf has no neighbours yet.
m.assert_edge_shared(v0, v1, 1)   # e2 boundary
m.assert_edge_shared(v1, v2, 1)   # e1 boundary
m.assert_edge_shared(v0, v2, 1)   # e3 boundary

# Triangle is non-degenerate (positive area; equilateral side=2 → area≈1.732).
m.assert_triangle_area_lt(tf, 5.0)
