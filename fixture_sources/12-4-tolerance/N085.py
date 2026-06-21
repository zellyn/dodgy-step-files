"""N085 — ShapeAnalysis_Edge.CheckPoints precision-asymmetry

Vertex tolerances differ by 10x; CheckPoints averages the precision implicitly,
using a single tolerance for both sides. Condition P1A.SquareDistance(P2A) <=
preci1² && P1B.SquareDistance(P2B) <= preci2² conflates two independent
tolerances; no mixed-tolerance path.

Fixture: Edge with vertices V1_tight (tol=0.001) and V2_loose (tol=0.01);
CheckPoints computes average tolerance, masking asymmetric precision requirements.

Byte assertions:
  contains(b'V1_tight')
  contains(b'V2_loose')
  contains(b'edge_asymmetric_tolerance')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N085",
    defect=(
        "edge_asymmetric_tolerance from V1_tight (tol=0.001) to V2_loose (tol=0.01); "
        "CheckPoints conflates preci1 and preci2 into single averaged tolerance — "
        "asymmetric precision requirements masked"
    ),
)

# Edge with asymmetric vertex tolerances
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))

v0 = f.vertex_point(p0, name="V1_tight")   # tol=0.001
v1 = f.vertex_point(p1, name="V2_loose")   # tol=0.01

d_x = f.direction((1.0, 0.0, 0.0))
vec_x = f.vector(d_x, 1.0)
l1 = f.line(p0, vec_x)
e1 = f.edge_curve(v0, v1, l1, name="edge_asymmetric_tolerance")

# Close with a rectangular face
p2 = f.cartesian_point((10.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

e_up   = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e_back = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
e_down = f.edge_curve(v3, v0, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

loop = f.edge_loop([
    f.oriented_edge(e1, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_down, True),
])
fob = f.face_outer_bound(loop)

d_z = f.direction((0.0, 0.0, 1.0))
plc = f.axis2_placement_3d(p0, d_z, f.direction((1.0, 0.0, 0.0)))
plane = f.plane(plc)
face = f.advanced_face([fob], plane)
shell = f.closed_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N085.stp")
