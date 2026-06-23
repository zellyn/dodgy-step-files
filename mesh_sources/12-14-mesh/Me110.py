"""Me110 — intersects_full_vertex_coincidence: identical triangles are not flagged as intersecting.

MeshFix `Triangle.intersects` Branch 2 (*FULL_VERTEX_COINCIDENCE*):
'if (eq1 && eq2 && eq3) return false' — when all three vertex pairs of
t1 coincide with t2's vertices (triangles are identical), the function
returns false. Coincident/duplicate triangles are not considered an
intersection for repair purposes; they are handled by the separate
merge-duplicate-polygons pass.

Geometric signature: two triangles referencing the exact same three vertex
indices — the degenerate case of a duplicate triangle using shared index
entries. MeshFix's intersects predicate exits at Branch 2 before any
geometry test.

Geometry:
  Shared positions: v0=(0,0,0), v1=(1,0,0), v2=(0,1,0)
  t0 = (v0, v1, v2)   — first entry
  t1 = (v0, v1, v2)   — exact duplicate (same indices)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me110",
             title="intersects_full_vertex_coincidence: exact duplicate triangles — Branch 2 returns false (not an intersection)",
             defect_class="duplicate_triangle_same_indices")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.0, 1.0, 0.0)

t0 = m.triangle(v0, v1, v2)
t1 = m.triangle(v0, v1, v2)   # exact same indices — genuine duplicate entry

# The two triangle entries are exact duplicates (same index triple).
m.assert_duplicate_triangle_pair(t0, t1)

# Each edge is incident on exactly 2 triangles because of the duplicate.
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v1, v2, 2)
