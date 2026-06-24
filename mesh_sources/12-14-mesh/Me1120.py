"""Me1120 — cross-CC external SI: two CCs whose members intersect each other (not internally).

CGAL PMP.remove_self_intersections Branch 6 @ line 2150 — *internal-vs-external-si-classification*:
  'if (does_self_intersect(cc)) { ... } else { if (!treat_all_CCs) continue; }'
  — for each connected component the dispatcher queries whether the SI is internal
  (within that CC) or involves faces from a *different* CC. When treat_all_CCs=false
  and a CC has no internal SI, it is skipped; when the SI crosses CC boundaries it
  is classified as external and both CCs are implicated.

Defect pattern: CC-A contains triangle 0 (in XY plane at origin). CC-B contains
  triangle 1 (tilted through XY plane, crossing tri 0). The two CCs share no vertices
  so the self-intersection is external/cross-CC (between CCs), not internal (within a CC).
  A third isolated clean triangle (tri 2, CC-C) is 20 units away and is entirely clean.
  This layout forces the classification branch to distinguish:
    - CC-A: no internal SI — but implicated externally by CC-B
    - CC-B: no internal SI — but it crosses into CC-A
    - CC-C: no SI at all
  When treat_all_CCs=false, the classifier must still surface both CC-A and CC-B
  because the external crossing touches both.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1120",
             title="cross-CC external SI: CC-A and CC-B intersect each other, no intra-CC SI",
             defect_class="self_intersection_cross_cc")

# CC-A: flat triangle in the XY plane (z=0).
a0 = m.vertex(0.0, 0.0, 0.0)   # 0
a1 = m.vertex(2.0, 0.0, 0.0)   # 1
a2 = m.vertex(1.0, 2.0, 0.0)   # 2
m.triangle(a0, a1, a2)   # tri 0 — CC-A, in z=0 plane

# CC-B: triangle that pierces the XY plane, crossing CC-A's tri 0.
# No shared vertices with CC-A; entirely disconnected.
b0 = m.vertex(1.0, 0.5, -1.0)  # 3 — below z=0
b1 = m.vertex(0.5, 0.5,  1.0)  # 4 — above z=0
b2 = m.vertex(1.5, 0.5,  1.0)  # 5 — above z=0
m.triangle(b0, b1, b2)   # tri 1 — CC-B, spans z=-1..+1, crosses tri 0

# CC-C: clean isolated triangle 20 units away, no SI.
c0 = m.vertex(0.0, 20.0, 0.0)  # 6
c1 = m.vertex(1.0, 20.0, 0.0)  # 7
c2 = m.vertex(0.5, 21.0, 0.0)  # 8
m.triangle(c0, c1, c2)   # tri 2 — CC-C, clean

# Assert: cross-CC external SI between tri 0 (CC-A) and tri 1 (CC-B).
m.assert_triangles_self_intersect(0, 1)

# Assert: CC-A and CC-C are disconnected (confirm separate CCs).
m.assert_triangle_not_reachable_from(2, 0)

# Assert: CC-B and CC-C are also disconnected.
m.assert_triangle_not_reachable_from(2, 1)
