"""N119 — ShapeFix_ShapeTolerance.LimitTolerance with-very-large-shape

Shape with coordinates at 1e10 scale; LimitTolerance's relative comparison
underflows because input tolerance has no scale awareness. A tolerance of 1.0
is reasonable for coords at 1e10 (relative precision 1e-10), but relative
checks like (tol / MAX_COORD) underflow to zero, causing the method to reject
valid tolerances and report spurious violations.

Reproducer: single edge at (1e10, 1e10, 1e10) to (1e10, 1e10+1, 1e10) with
nominal tolerance 1.0. LimitTolerance's internal relative ratio test underflows,
flagging this as an invalid tolerance configuration.

Byte assertions:
  contains(b'edge_at_1e10_scale')
  contains(b'v_huge_0')
  contains(b'v_huge_1')

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N119",
    defect=(
        "OPEN_SHELL face with edge_at_1e10_scale from v_huge_0 to v_huge_1 "
        "at coordinates (1e10, 1e10, 1e10); tolerance 1.0 is valid relatively "
        "but LimitTolerance relative ratio test underflows — spurious violation"
    ),
)

# Huge-scale geometry
large = 1.0E10
p0 = f.cartesian_point((large, large, large))
p1 = f.cartesian_point((large, large + 1.0, large))

v_huge_0 = f.vertex_point(p0, name="v_huge_0")
v_huge_1 = f.vertex_point(p1, name="v_huge_1")

d_y = f.direction((0.0, 1.0, 0.0))
vec_y = f.vector(d_y, 1.0)
l_huge = f.line(p0, vec_y)
e_huge = f.edge_curve(v_huge_0, v_huge_1, l_huge, name="edge_at_1e10_scale")

# Close with a face
p2 = f.cartesian_point((large + 1.0, large + 1.0, large))
p3 = f.cartesian_point((large + 1.0, large, large))
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

e_right = f.edge_curve(v_huge_1, v2, f.line(p1, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
e_back  = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))
e_left  = f.edge_curve(v3, v_huge_0, f.line(p3, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))

loop = f.edge_loop([
    f.oriented_edge(e_huge, True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_left, True),
], name="huge_loop")
fob = f.face_outer_bound(loop)

zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p0, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([fob], plane)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
# Tolerance of 1.0 is reasonable at 1e10 scale (relative: 1e-10)
f.add_product_chain(sbsm, uncertainty=1.0)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N119.stp")
