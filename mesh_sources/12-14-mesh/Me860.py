"""Me860 — strongIntersectionRemoval intersection-detection trigger: selectIntersectingTriangles returns non-empty.

Catalog claim: a mesh with exactly one self-intersecting triangle pair causes
Basic_TMesh.strongIntersectionRemoval to detect a non-empty set via
selectIntersectingTriangles() and enter the removal loop (Branch 1). Without
any SI, the function exits immediately with success; this fixture ensures the
detection branch fires by placing two genuinely crossing triangles.

Source: MeshFix `Basic_TMesh.strongIntersectionRemoval` Branch 1 @ line 381 —
*Intersection-detection trigger*: selectIntersectingTriangles() returns
non-empty; enters the iterative SI removal loop.

Defect carrier: triangle 0 lies in the XY plane. Triangle 1 is a crossing
triangle whose edge spans from above to below z=0, piercing triangle 0 through
its interior. The SI oracle confirms the pair intersects. Two additional clean
triangles (2 and 3) provide context geometry that is not intersecting.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me860",
    title="strongIntersectionRemoval intersection-detection trigger: selectIntersectingTriangles non-empty (Branch 1)",
    defect_class="self_intersection",
)

# Triangle 0: flat base in XY plane.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2

# Triangle 1: intruder crossing tri 0 — spans z=-1 to z=+1 through center.
v3 = m.vertex(1.0, 0.8,  1.0)  # 3 — above z=0
v4 = m.vertex(1.0, 0.8, -1.0)  # 4 — below z=0 (defect: pierces tri 0)
v5 = m.vertex(0.0, 0.8,  0.0)  # 5 — in z=0 plane, outside tri 0's interior

m.triangle(v0, v1, v2)   # tri 0 — XY base
m.triangle(v3, v4, v5)   # tri 1 — crosses tri 0

# Two clean context triangles 30 units away — not intersecting anything.
v6 = m.vertex(0.0, 30.0, 0.0)  # 6
v7 = m.vertex(1.0, 30.0, 0.0)  # 7
v8 = m.vertex(1.0, 31.0, 0.0)  # 8
v9 = m.vertex(0.0, 31.0, 0.0)  # 9

m.triangle(v6, v7, v8)   # tri 2 — clean
m.triangle(v6, v8, v9)   # tri 3 — clean

# Assert: the crossing pair is detected as self-intersecting.
m.assert_triangles_self_intersect(0, 1)

# Assert: clean triangles do not intersect each other.
m.assert_triangles_do_not_intersect(2, 3)

# Assert: SI pair unreachable from clean patch (separate CCs).
m.assert_triangle_not_reachable_from(2, 0)
