"""N053 — ShapeAnalysis_ShapeTolerance.AddTolerance polarity asymmetry

AddTolerance accumulates tolerance array myTols[0..2] with asymmetric
comparisons: myTols[0] (minimum) checked with > operator (upper-bound
semantics) while myTols[2] (maximum) checked with < operator (lower-bound
semantics). This inverts the intended meaning of min/max boundaries, causing
in-range tolerances to be rejected when the asymmetry dominates.

Reproducer: Call AddTolerance on shape with edge tolerance 0.0015 and bounds
[0.001, 0.002]. Asymmetric comparisons (myTols[0] > cmin vs myTols[2] < cmax)
cause nondeterministic rejection despite in-range value.

Byte assertions:
  contains(b'v_min_bound')
  contains(b'v_max_bound')
  count_entity_def(b'VERTEX_POINT') == 3

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N053",
    defect=(
        "PLANE face with vertices at tolerance bounds 0.001 and 0.002; "
        "AddTolerance asymmetric comparisons: myTols[0]>cmin (upper-bound) "
        "vs myTols[2]<cmax (lower-bound) inverts min/max semantics"
    ),
)

# Single PLANE z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Three vertices: one at lower bound, one at upper bound, one nominal
# Vertex at min tolerance boundary 0.001
pa = f.cartesian_point((0.0, 0.0, 0.0))
va = f.vertex_point(pa, name="v_min_bound")

# Vertex at max tolerance boundary 0.002
pb = f.cartesian_point((10.0, 0.0, 0.0))
vb = f.vertex_point(pb, name="v_max_bound")

# Vertex with nominal tolerance 0.0015 (within [0.001, 0.002])
pc = f.cartesian_point((5.0, 8.66, 0.0))
vc = f.vertex_point(pc, name="v_nominal")

# Edge from min to max boundary vertices
d1 = f.direction((1.0, 0.0, 0.0))
v1 = f.vector(d1, 1.0)
l1 = f.line(pa, v1)
e1 = f.edge_curve(va, vb, l1, name="edge_boundary")

d2 = f.direction((-0.5, 0.866, 0.0))
v2 = f.vector(d2, 1.0)
l2 = f.line(pb, v2)
e2 = f.edge_curve(vb, vc, l2, name="e2")

d3 = f.direction((-0.5, -0.866, 0.0))
v3 = f.vector(d3, 1.0)
l3 = f.line(pc, v3)
e3 = f.edge_curve(vc, va, l3, name="e3")

loop = f.edge_loop([
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="face_asymmetric_tol")

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N053.stp")
