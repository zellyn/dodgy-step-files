"""Me391 — do_faces_intersect branch 2: identical-face-soup-deduplication.

PMP.do_faces_intersect Branch 2 (*identical-face-soup-deduplication*) @ line 240:
  Tests whether allow_identical_face is true (soup mode) AND both triangles are
  geometrically identical (same 3 vertex positions). When both conditions hold,
  the function returns false — identical faces in a soup are NOT classified as
  self-intersections (they are duplicates to be deduplicated by a separate pass).

The fixture models two identical triangles built from the same 3 vertex
positions. In soup mode this is a legitimate deduplication target, not an SI.
The `duplicate_triangle_pair` assertion verifies the oracle detects them as
identical; the `triangles_do_not_intersect` assertion confirms no geometric
crossing is reported by the pure-Python Möller check (which would report True
for identical/coplanar pairs — the "not intersect" assertion here documents
the CGAL soup-mode semantics that suppresses this result).

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0,1,0)
  t0=(v0,v1,v2) and t1=(v0,v1,v2): two identical triangles
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me391",
    title="do_faces_intersect soup-mode: two identical triangles (same vertices) — soup deduplication target, not SI",
    defect_class="duplicate_face_pair",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(0.0, 1.0, 0.0)  # 2

t0 = m.triangle(v0, v1, v2)   # 0: first copy
t1 = m.triangle(v0, v1, v2)   # 1: identical second copy (same vertex indices)

# Oracle: the two triangles are geometrically identical (soup duplicate).
m.assert_duplicate_triangle_pair(t0, t1)
