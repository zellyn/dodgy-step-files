"""Me301 — retriangulateSelectedRegion_normal_orientation_conflict: triangle normal opposes region normal, abort.

MeshFix `Basic_TMesh.retriangulateSelectedRegion` Branch 2 (*normal_orientation_conflict*) @ line 966:
  `if (u->getNormal()*nor <= 0.0) { ... return; }` — a triangle in the selected
  region has a normal anti-parallel to the accumulated region normal. Retriangulation
  is aborted with a warning because the geometry is too complex (non-orientable or
  saddle-shaped) for the Delaunay approach.

The algorithm accumulates a consensus normal `nor` from the region triangles.
When any individual triangle's normal dot-products to <= 0 with the consensus,
the region has a conflicting orientation — the abort fires.

Defect carrier: a selected region of two adjacent triangles that fold backward
such that one triangle's normal is anti-parallel to the other's. The consensus
normal derived from triangle 0 is +Z; triangle 1's normal is -Z.

Geometry (flat XY plane, with one inverted triangle):
  t0 = (v0, v1, v2) — CCW, normal = +Z
  t1 = (v2, v1, v3) — CW (inverted), normal = -Z

Both triangles form the selected region. Their normals conflict: dot < 0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me301",
    title="retriangulateSelectedRegion_normal_orientation_conflict: region normals conflict, abort (Branch 2)",
    defect_class="retriangulate_region_orientation_conflict",
)

# Four vertices; two adjacent triangles with conflicting normals.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2
v3 = m.vertex(3.0, 2.0, 0.0)   # 3

# t0 = CCW in XY plane → normal = +Z
t0 = m.triangle(v0, v1, v2)   # 0: normal = +Z

# t1 = CW in XY plane → normal = -Z (orientation conflict with t0).
# In MeshFix, when building `nor` from t0 then checking t1: nor ≈ +Z,
# and t1->getNormal() = -Z, so dot <= 0 → abort.
t1 = m.triangle(v2, v3, v1)   # 1: normal = -Z (CW winding)

# Shared edge (v1,v2) is interior.
m.assert_edge_shared(v1, v2, 2)   # shared by t0 and t1

# The two triangles have inconsistent winding — normal dot < 0.
# This is the exact condition retriangulateSelectedRegion Branch 2 checks.
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)
