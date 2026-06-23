"""Me020 — SI within single CC vs across two CCs (internal vs external classification).

Catalog claim: the mesh has two connected components. Within CC A (triangles 0,1),
two triangles self-intersect. CC B (triangles 2,3) is clean. The healer's SI
classification branch (internal vs external) determines whether to invoke
does_self_intersect on each CC individually before deciding to process it.

Source: CGAL PMP.remove_self_intersections Branch 6 @ line 2150 —
*internal-vs-external-si-classification*: whether self-intersections exist within
a CC (internal) or only across CCs (external); controls whether the CC is processed
when treat_all_CCs=false.

Defect carrier: CC A has an internal self-intersection (triangles 0 and 1 in
crossing planes). CC B is a clean flat quad 30 units away with no SI. The fixture
emphasizes that the SI is purely internal to CC A — it cannot be classified as an
across-CC crossing because the CCs have no shared vertices.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me020",
             title="internal SI in CC-A only; CC-B clean: internal-vs-external SI classification",
             defect_class="self_intersection_internal_cc")

# CC A: crossing XY and XZ triangles (internal SI).
a0 = m.vertex(0.0, 0.0, 0.0)   # 0 — shared apex of crossing pair
a1 = m.vertex(1.0, 1.0, 0.0)   # 1
a2 = m.vertex(1.0, -1.0, 0.0)  # 2
a3 = m.vertex(1.0, 0.0, 1.0)   # 3
a4 = m.vertex(1.0, 0.0, -1.0)  # 4
m.triangle(a0, a1, a2)    # tri 0 — CC A, in XY plane
m.triangle(a0, a3, a4)    # tri 1 — CC A, in XZ plane; crosses tri 0

# CC B: clean flat patch 30 units away.
b0 = m.vertex(0.0, 30.0, 0.0)  # 5
b1 = m.vertex(1.0, 30.0, 0.0)  # 6
b2 = m.vertex(1.0, 31.0, 0.0)  # 7
b3 = m.vertex(0.0, 31.0, 0.0)  # 8
m.triangle(b0, b1, b2)    # tri 2 — CC B, clean
m.triangle(b0, b2, b3)    # tri 3 — CC B, clean

# Assert: internal SI within CC A.
m.assert_triangles_self_intersect(0, 1)

# Assert: CC B unreachable from CC A (confirms separate CCs, no cross-CC SI).
m.assert_triangle_not_reachable_from(2, 0)
