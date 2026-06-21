"""N110 — ShapeAnalysis_Edge.CheckPoints precision-vs-projection-distance

CheckPoints called with precision 1e-3 but projection-distance test uses 1e-6
internally. Verdict based on smaller internal threshold contradicts caller's
tolerance specification. Long linear edge (100mm) tests precision asymmetry
in point-pair distance evaluation.

Byte assertions:
  contains(b'test_edge')
  contains(b'v_start')
  contains(b'v_end')
  contains(b'test_face')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N110",
    defect=(
        "CLOSED_SHELL check_shell with test_face containing test_edge (v_start→v_end, "
        "100mm); CheckPoints uses precision 1e-3 but projection-distance test applies "
        "1e-6 internally — verdict contradicts caller tolerance specification"
    ),
)

# Long 100mm edge
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((100.0, 0.0, 0.0))
p2 = f.cartesian_point((100.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v_start = f.vertex_point(p0, name="v_start")
v_end = f.vertex_point(p1, name="v_end")
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

d_x = f.direction((1.0, 0.0, 0.0))
vec_x = f.vector(d_x, 100.0)
l_long = f.line(p0, vec_x)
e_test = f.edge_curve(v_start, v_end, l_long, name="test_edge")

e_up   = f.edge_curve(v_end, v2, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e_back = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 100.0)))
e_down = f.edge_curve(v3, v_start, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

loop = f.edge_loop([
    f.oriented_edge(e_test, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_down, True),
], name="check_loop")
fob = f.face_outer_bound(loop)

zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p0, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([fob], plane, name="test_face")

shell = f.closed_shell([face], name="check_shell")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, uncertainty=1.0E-6)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N110.stp")
