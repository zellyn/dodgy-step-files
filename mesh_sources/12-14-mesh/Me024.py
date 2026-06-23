"""Me024 — SI region compactifies to a single face (singleton-CC rejection).

Catalog claim: after the bounding-box / OBB compactification step collapses a
self-intersecting cluster, only a single triangle remains in the candidate CC.
The algorithm detects cc_faces.size() == 1 and skips further processing (continue
in the main loop) because there is no hole topology to fill.

Source: CGAL PMP.remove_self_intersections Branch 14 @ line 2135 —
*singleton-cc-rejection*: whether compactified region consists of single face
only; skip further processing when true.

Defect carrier: a single isolated triangle (tri 0) whose bounding box overlaps
a second triangle (tri 1) but whose only possible SI region — after intersection
detection narrows to the single-face level — contains just that one face. Tri 1
genuinely self-intersects tri 0 (so SI is detected), but the CC around the crossing
point that passes the face-size filter has exactly 1 face before expansion.
The fixture uses the minimal 2-triangle cross with no surrounding context.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me024",
             title="SI with singleton compactified region: cc_faces.size()==1 branch",
             defect_class="self_intersection_singleton_cc")

# Two crossing triangles with no belt — the SI cluster compactifies to 1 face
# on each side because there are no neighboring triangles to include.

# Triangle 0: in XY plane.
v0 = m.vertex(0.0,  0.0, 0.0)   # 0
v1 = m.vertex(1.0,  1.0, 0.0)   # 1
v2 = m.vertex(1.0, -1.0, 0.0)   # 2
m.triangle(v0, v1, v2)    # tri 0 — XY

# Triangle 1: in XZ plane, crossing tri 0.
v3 = m.vertex(1.0, 0.0,  1.0)   # 3
v4 = m.vertex(1.0, 0.0, -1.0)   # 4
m.triangle(v0, v3, v4)    # tri 1 — XZ; crosses tri 0

# Assert: the minimal SI.
m.assert_triangles_self_intersect(0, 1)
