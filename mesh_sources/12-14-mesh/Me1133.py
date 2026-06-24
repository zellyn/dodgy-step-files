"""Me1133 — SI region compactifies to a single face: singleton-CC rejection branch.

Catalog claim: after bounding-box compactification of a self-intersecting
cluster, exactly one triangle remains in the candidate connected component
(cc_faces.size() == 1). The algorithm detects this singleton condition and
issues a `continue` in the main loop, skipping further hole-fill processing
because there is no surrounding topology to repair.

Source: CGAL PMP.remove_self_intersections Branch 14 @ line 2135 —
*singleton-cc-rejection*: whether compactified region consists of single face
only; skip further processing when true.

Defect carrier: a minimal two-triangle crossing (XY and XZ planes, shared apex
at origin) with no surrounding belt or context triangles. After SI detection
and bounding-box compactification, each side of the crossing reduces to a
single-face CC. The smallest such CC has cc_faces.size() == 1, which triggers
the singleton skip. The fixture uses a rotated apex position to distinguish
itself from Me024 while exercising the same branch.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1133",
             title="SI with singleton compactified region (cc_faces.size()==1): skip branch",
             defect_class="self_intersection_singleton_cc")

# Two crossing triangles with no belt — each side is a singleton CC.
# Triangle 0: tilted in XY plane (apex offset to distinguish from Me024).
v0 = m.vertex(0.5, 0.5,  0.0)   # 0 — shared crossing apex
v1 = m.vertex(1.5, 1.5,  0.0)   # 1
v2 = m.vertex(1.5, -0.5, 0.0)   # 2
m.triangle(v0, v1, v2)    # tri 0 — in XY-ish plane

# Triangle 1: pierces tri 0 by straddling z=0 through its centroid.
# Centroid of tri 0 ≈ (1.167, 0.5, 0)
v3 = m.vertex(1.167, 0.5,  1.0)   # 3 — above centroid
v4 = m.vertex(1.167, 0.5, -1.0)   # 4 — below centroid
v5 = m.vertex(2.0,   0.5,  0.0)   # 5 — in z=0 plane, outside
m.triangle(v3, v4, v5)    # tri 1 — crosses tri 0 at centroid

# Assert: SI present (tris 0 and 1 cross).
m.assert_triangles_self_intersect(0, 1)
