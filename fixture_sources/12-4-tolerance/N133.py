"""N133 — ShapeFix_ShapeTolerance negative precision acceptance

SetTolerance(shape, prec, VERTEX) accepts negative or zero precision without
validation, silently producing TVertex::Tolerance(-0.5) and corrupting
downstream operations.

Reproducer: shape with v_neg_tol_candidate vertex; SetTolerance called with
prec=-0.5 accepted without error, negative tolerance corrupts downstream.

Byte assertions:
  contains(b'v_neg_tol_candidate')
  contains(b'ec1')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N133",
    defect=(
        "CLOSED_SHELL with face containing v_neg_tol_candidate; SetTolerance "
        "accepts prec=-0.5 without validation — creates negative tolerance, "
        "corrupting downstream operations with no precondition check"
    ),
)

# Rectangular face with the candidate vertex for negative tolerance
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v_neg = f.vertex_point(p0, name="v_neg_tol_candidate")
v2 = f.vertex_point(p1, name="v2")
v3 = f.vertex_point(p2)
v4 = f.vertex_point(p3)

ec1 = f.edge_curve(v_neg, v2, f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)), name="ec1")
e_up   = f.edge_curve(v2, v3, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e_back = f.edge_curve(v3, v4, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e_down = f.edge_curve(v4, v_neg, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

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

shell = f.closed_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N133.stp")
