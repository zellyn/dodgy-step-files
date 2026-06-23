"""Me018 — SI pocket resolvable by smoothing (use_smoothing branch).

Catalog claim: a flat patch (triangles 0,1) is pierced by an extra triangle
(triangle 2) whose apex has been displaced below the patch plane. Moving the
apex back to z=0 via a smoothing pass would resolve the self-intersection without
topology change — this exercises the smoothing-based healing path.

Source: CGAL PMP.remove_self_intersections Branch 3 @ line 2397 —
*smoothing-phase-strategy*: branch to smoothing-based healing (use_smoothing NP)
vs the default hole-fill approach.

Defect carrier: triangles 0 and 1 form a flat patch in the z=0 plane. Triangle 2
spans z=+0.5 (two upper vertices) to z=-0.5 (displaced apex), so it crosses the
z=0 patch. The offending apex at (1,1,-0.5) is the smoothing target — nudging it
back to z=0 would eliminate the crossing.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me018",
             title="SI pocket with displaced apex piercing flat patch: use_smoothing branch",
             defect_class="self_intersection_smoothable")

# Flat patch in z=0 plane.
p0 = m.vertex(0.0, 0.0, 0.0)   # 0
p1 = m.vertex(2.0, 0.0, 0.0)   # 1
p2 = m.vertex(2.0, 2.0, 0.0)   # 2
p3 = m.vertex(0.0, 2.0, 0.0)   # 3
m.triangle(p0, p1, p2)   # tri 0 — flat patch triangle A
m.triangle(p0, p2, p3)   # tri 1 — flat patch triangle B

# Intruding triangle: two upper vertices above the patch, one apex below.
# Apex at (1,1,-0.5) is the "wrongly displaced" vertex that a smoother would fix.
s0 = m.vertex(1.0, -0.5, 0.5)  # 4
s1 = m.vertex(1.0,  2.5, 0.5)  # 5
s2 = m.vertex(1.0,  1.0, -0.5) # 6 — displaced apex (defect)
m.triangle(s0, s1, s2)   # tri 2 — slices through patch from above to below

# Assert: tri 0 and tri 2 self-intersect (the intruding triangle pierces the patch).
m.assert_triangles_self_intersect(0, 2)
