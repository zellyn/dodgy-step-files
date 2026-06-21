"""N116 — ShapeFix_Edge.FixVertexTolerance shared-by-many-edges

Vertex used by 4+ edges; FixVertexTolerance iterates per-edge but writes back
to the shared vertex, overwriting previous results. Final tolerance reflects
only the last edge that touched it, losing constraints from earlier edges.
Each iteration recalculates and overwrites without accumulating maxima.

Reproducer: star topology with a central hub vertex shared by 4 radial edges,
each demanding a different tolerance (1e-2, 1e-3, 1e-4, 1e-5). Algorithm
processes edges in order, overwriting hub's tolerance 4 times. Downstream
operations see only the last (1e-5) value instead of the maximum (1e-2).

Byte assertions:
  contains(b'hub')
  contains(b'e1_1e-2')
  contains(b'e2_1e-3')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N116",
    defect=(
        "Star topology: hub vertex shared by e1_1e-2, e2_1e-3, e3_1e-4, e4_1e-5; "
        "FixVertexTolerance overwrites hub tolerance on each edge pass without taking "
        "max — final value is 1e-5 (last), not 1e-2 (required max)"
    ),
)

# Hub vertex at origin
p_hub = f.cartesian_point((0.0, 0.0, 0.0), name="shared_hub")
hub = f.vertex_point(p_hub, name="hub")

# 4 radial spoke vertices
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((0.0, 10.0, 0.0))
p3 = f.cartesian_point((-10.0, 0.0, 0.0))
p4 = f.cartesian_point((0.0, -10.0, 0.0))

v1 = f.vertex_point(p1, name="v1")
v2 = f.vertex_point(p2, name="v2")
v3 = f.vertex_point(p3, name="v3")
v4 = f.vertex_point(p4, name="v4")

# 4 edges from hub to each spoke
d_px = f.direction((1.0, 0.0, 0.0))
d_py = f.direction((0.0, 1.0, 0.0))
d_nx = f.direction((-1.0, 0.0, 0.0))
d_ny = f.direction((0.0, -1.0, 0.0))

e1 = f.edge_curve(hub, v1, f.line(p_hub, f.vector(d_px, 10.0)), name="e1_1e-2")
e2 = f.edge_curve(hub, v2, f.line(p_hub, f.vector(d_py, 10.0)), name="e2_1e-3")
e3 = f.edge_curve(hub, v3, f.line(p_hub, f.vector(d_nx, 10.0)), name="e3_1e-4")
e4 = f.edge_curve(hub, v4, f.line(p_hub, f.vector(d_ny, 10.0)), name="e4_1e-5")

# Form a rectangular face using a outer loop
# (hub sits inside, but edges form the connectivity)
# Build a square face at the boundary: v1→v2→v3→v4→v1
e_12 = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction((-1.0, 1.0, 0.0)), 10.0)))
e_23 = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, -1.0, 0.0)), 10.0)))
e_34 = f.edge_curve(v3, v4, f.line(p3, f.vector(f.direction((1.0, -1.0, 0.0)), 10.0)))
e_41 = f.edge_curve(v4, v1, f.line(p4, f.vector(f.direction((1.0, 1.0, 0.0)), 10.0)))

loop = f.edge_loop([
    f.oriented_edge(e_12, True),
    f.oriented_edge(e_23, True),
    f.oriented_edge(e_34, True),
    f.oriented_edge(e_41, True),
])
fob = f.face_outer_bound(loop)

zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p_hub, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([fob], plane)

shell = f.closed_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N116.stp")
