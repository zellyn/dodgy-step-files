"""N051 — ShapeAnalysis_ShapeTolerance.InTolerance vertex polarity inversion

InTolerance filters vertices by tolerance range [valmin, valmax] using an
inverted comparison (tol >= valmax) instead of the correct (tol <= valmax).
This contradicts the FACE and EDGE branches which correctly use (tol <= valmax),
causing in-range vertices to be rejected while out-of-range vertices are selected.

Reproducer: Call InTolerance(shape, 0.001, 0.002, TopAbs_VERTEX) on a shape
with vertices at tol=0.0015 (in-range) and tol=0.005 (out-of-range). Buggy
result returns only the 0.005 vertex; correct result returns only the 0.0015 vertex.

Byte assertions:
  contains(b'v_in_range')
  contains(b'v_out_range')
  count_entity_def(b'VERTEX_POINT') == 3

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N051",
    defect=(
        "PLANE face with two vertices: v_in_range (tol=0.0015) and "
        "v_out_range (tol=0.005); InTolerance inverted comparison (>= valmax) "
        "selects out-of-range vertex and rejects in-range vertex"
    ),
)

# Single PLANE z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Three vertices forming a triangle
# Vertex A at tol=0.0015 (within [0.001, 0.002] range)
pa = f.cartesian_point((0.0, 0.0, 0.0))
va = f.vertex_point(pa, name="v_in_range")

# Vertex B at tol=0.005 (outside [0.001, 0.002] range)
pb = f.cartesian_point((5.0, 0.0, 0.0))
vb = f.vertex_point(pb, name="v_out_range")

# Vertex C to complete triangle
pc = f.cartesian_point((2.5, 4.33, 0.0))
vc = f.vertex_point(pc, name="v_third")

# Edges forming triangular boundary loop
d1 = f.direction((1.0, 0.0, 0.0))
v1 = f.vector(d1, 1.0)
l1 = f.line(pa, v1)
e1 = f.edge_curve(va, vb, l1, name="e1")

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
face = f.advanced_face([fob], plane, name="face_with_polarity_bug")

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N051.stp")
