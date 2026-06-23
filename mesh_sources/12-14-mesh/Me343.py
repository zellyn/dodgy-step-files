"""Me343 — init_triangle_copy_iteration: triangle count drives FOREACHVTTRIANGLE loop in init.

MeshFix `Basic_TMesh.init` Branch 4 (*TRIANGLE_COPY_ITERATION*) @ line 205:
  'FOREACHVTTRIANGLE((&tin->T), t, n) { ... newTriangle(...); t->info = nt; }' — iterates
  through all triangles and creates a clone triangle per entry with a back-pointer in t->info.
  Degenerate triangles (zero area — all three vertices collinear or coincident) are still
  inserted into the triangle list and must be iterated.

Defect pattern: a mix of 2 valid triangles and 1 degenerate (zero-area) triangle.
  The degenerate triangle t2 has v0, v1, v2 on the same line — area ≈ 0. Branch 4
  fires for all 3 entries including the degenerate one.

Geometry: v0=(0,0,0), v1=(1,0,0), v2=(2,0,0) — collinear; v3=(0.5,1,0), v4=(1,0,0) alias.
  t0=(v0,v3,v1) — valid; t1=(v1,v3,v0) control; t2=(v0,v1,v2) — degenerate (collinear).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me343",
             title="init_triangle_copy_iteration: degenerate zero-area triangle forces FOREACHVTTRIANGLE over 3 entries",
             defect_class="degenerate_triangle")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(2.0, 0.0, 0.0)   # collinear with v0 and v1 along X-axis
v3 = m.vertex(0.5, 1.0, 0.0)

t0 = m.triangle(v0, v3, v1)   # 0: valid triangle
t1 = m.triangle(v0, v1, v2)   # 1: degenerate — v0, v1, v2 are collinear, area = 0

m.assert_triangle_area_lt(1, 1e-9)

# All edges of the degenerate triangle are boundary (open mesh).
m.assert_edge_shared(v0, v1, 2)   # shared between t0 and t1
m.assert_edge_shared(v1, v2, 1)   # only t1
m.assert_edge_shared(v0, v2, 1)   # only t1
