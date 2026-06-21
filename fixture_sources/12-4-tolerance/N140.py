"""N140 — ShapeAnalysis_Surface.Continuity.tolerance_interval_mismatch

Surface continuity check omits boundary tolerance scaling. Parameter interval
alignment (gap=0.001 vs tol base=1e-7) ignores scale; near-matching patches
falsely pass continuity despite parameter misalignment.

Reproducer: face with ec1 (edge1_surf1, v1→v2) and ec2 (edge2_surf2, v3→v4)
representing two surface patches; continuity check omits boundary tolerance
scaling at parameter domain boundary.

Byte assertions:
  contains(b'v1')
  contains(b'v2')
  contains(b'ec1')
  contains(b'ec2')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N140",
    defect=(
        "CLOSED_SHELL with face containing ec1 (edge1_surf1: v1→v2) and ec2 "
        "(edge2_surf2: v3→v4); surface continuity check omits boundary tolerance "
        "scaling — 0.001 parameter gap vs 1e-7 base tolerance ignored, false pass"
    ),
)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v1 = f.vertex_point(p0, name="v1")
v2 = f.vertex_point(p1, name="v2")
v3 = f.vertex_point(p2, name="v3")
v4 = f.vertex_point(p3, name="v4")

ec1 = f.edge_curve(v1, v2, f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)), name="ec1")
ec2 = f.edge_curve(v3, v4, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)), name="ec2")
e_up   = f.edge_curve(v2, v3, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e_down = f.edge_curve(v4, v1, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

loop = f.edge_loop([
    f.oriented_edge(ec1, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(ec2, True),
    f.oriented_edge(e_down, True),
])
fob = f.face_outer_bound(loop)

zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p0, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([fob], plane)

shell = f.closed_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N140.stp")
