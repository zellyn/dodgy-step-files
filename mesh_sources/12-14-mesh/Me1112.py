"""Me1112 — local vertex displacement producing SI resolvable by smoothing.

Tests precondition that NP use_smoothing would act on: a mesh where one vertex
has been displaced from its natural position causing a self-intersection that a
smoothing pass could repair by moving the vertex back — no topological change needed.

Source: CGAL PMP.remove_self_intersections Branch 3 @ line 2397 —
*smoothing-phase-strategy*: use_smoothing NP selects the smoothing-based repair
branch vs the default hole-fill approach. Branch fires when use_smoothing=true
and the SI pocket is amenable to vertex-position correction.

Geometry:
  Triangles 0,1,2 form a clean flat fan in the Z=0 plane around vertex 0.
  Triangle 3 shares vertex 5 with the fan; vertex 5 has been displaced to Z=-0.8,
  pulling tri 3 below the fan plane. The lower face of tri 3 intersects tri 0
  (the adjacent fan triangle). A smoothing pass that lifts vertex 5 back to Z=0
  would resolve the SI without any remeshing.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1112",
    title="displaced apex below flat fan causing SI: use_smoothing strategy branch",
    defect_class="self_intersection_smoothable",
)

# Flat fan of three triangles in Z=0 plane.
hub = m.vertex(0.0, 0.0, 0.0)   # 0 — fan center
r0  = m.vertex(1.0, 0.0, 0.0)   # 1
r1  = m.vertex(0.5, 1.0, 0.0)   # 2
r2  = m.vertex(-0.5, 1.0, 0.0)  # 3
r3  = m.vertex(-1.0, 0.0, 0.0)  # 4
m.triangle(hub, r0, r1)    # tri 0 — fan right
m.triangle(hub, r1, r2)    # tri 1 — fan center
m.triangle(hub, r2, r3)    # tri 2 — fan left

# Intruding triangle: one vertex correctly placed at Z=0, apex displaced to Z=-0.8.
# apex v5 is the smoothing target — moving it to Z=0 would fix the SI.
top = m.vertex(0.5, 2.0, 0.0)   # 5 — correct top vertex
apex = m.vertex(0.5, 1.0, -0.8) # 6 — displaced apex (defect); should be at Z=0
m.triangle(r1, top, apex)  # tri 3 — intruder crossing below fan plane; intersects tri 0

# Assert: the displaced apex causes tri 3 to cross tri 0.
m.assert_triangles_self_intersect(0, 3)
