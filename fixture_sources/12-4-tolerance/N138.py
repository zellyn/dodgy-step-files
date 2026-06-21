"""N138 — ShapeAnalysis_Edge.CheckPoints.tolerance_conservatism_fail

Conservative tolerance selection without endpoint validation. Tightest precision
bound chosen (1e-8) but not enforced on both endpoints. Precision-varying edges
(5e-7 sep > 1e-8 tol) incorrectly rejected.

Reproducer: edge ec1 (mixed_preci_edge from v1 to v2); conservative 1e-8
tolerance chosen but not validated at both endpoints, causing incorrect
rejection of valid edges with precision variation.

Byte assertions:
  contains(b'v1')
  contains(b'v2')
  contains(b'ec1')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N138",
    defect=(
        "CLOSED_SHELL shell with face containing ec1 (mixed_preci_edge from v1 to v2); "
        "CheckPoints selects conservative 1e-8 tolerance but doesn't validate both "
        "endpoints at that bound — 5e-7 sep > 1e-8 causes incorrect rejection"
    ),
)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v1 = f.vertex_point(p0, name="v1")
v2 = f.vertex_point(p1, name="v2")
v3 = f.vertex_point(p2)
v4 = f.vertex_point(p3)

ec1 = f.edge_curve(v1, v2, f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)), name="ec1")
e_up   = f.edge_curve(v2, v3, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e_back = f.edge_curve(v3, v4, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e_down = f.edge_curve(v4, v1, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

loop = f.edge_loop([
    f.oriented_edge(ec1, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_down, True),
])
fob = f.face_outer_bound(loop)

zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p0, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([fob], plane)

shell = f.closed_shell([face], name="shell")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N138.stp")
