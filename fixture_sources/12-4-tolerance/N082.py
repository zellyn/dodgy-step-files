"""N082 — ShapeAnalysis_ShapeTolerance.AddTolerance shape-type membership

AddTolerance(shape, type) where type is COMPOUND; AddTolerance's iteration
counts each sub-shape's tolerance once per containment level, leading to
phantom double-counts in nested structures.

Fixture: Two adjacent planar faces sharing an edge in an OPEN_SHELL; the
second face is also referenced in a standalone OPEN_SHELL causing double-count
in compound tolerance aggregation. When AddTolerance iterates over a compound
containing the same sub-shapes at multiple containment levels, tolerance values
accumulate phantom extra weight.

Byte assertions:
  contains(b'face1')
  contains(b'face2')
  count_entity_def(b'ADVANCED_FACE') == 2

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=accept(0)
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N082",
    defect=(
        "two ADVANCED_FACEs in OPEN_SHELL; AddTolerance iterates both the "
        "compound and its constituents, inflating tolerance aggregation by "
        "counting each sub-shape's tolerance once per containment level"
    ),
)

# First face: 1x5 rectangle
p_00 = f.cartesian_point((0.0, 0.0, 0.0))
p_10 = f.cartesian_point((1.0, 0.0, 0.0))
p_11 = f.cartesian_point((1.0, 5.0, 0.0))
p_01 = f.cartesian_point((0.0, 5.0, 0.0))

v_00 = f.vertex_point(p_00)
v_10 = f.vertex_point(p_10)
v_11 = f.vertex_point(p_11)
v_01 = f.vertex_point(p_01)

d_x = f.direction((1.0, 0.0, 0.0))
d_y = f.direction((0.0, 1.0, 0.0))
d_negx = f.direction((-1.0, 0.0, 0.0))
d_negy = f.direction((0.0, -1.0, 0.0))

vx1 = f.vector(d_x, 1.0)
vy5 = f.vector(d_y, 5.0)
vnx1 = f.vector(d_negx, 1.0)
vny5 = f.vector(d_negy, 5.0)

e_f1_bot = f.edge_curve(v_00, v_10, f.line(p_00, vx1))
e_f1_r   = f.edge_curve(v_10, v_11, f.line(p_10, vy5))
e_f1_top = f.edge_curve(v_11, v_01, f.line(p_11, vnx1))
e_f1_l   = f.edge_curve(v_01, v_00, f.line(p_01, vny5))

loop1 = f.edge_loop([
    f.oriented_edge(e_f1_bot, True),
    f.oriented_edge(e_f1_r, True),
    f.oriented_edge(e_f1_top, True),
    f.oriented_edge(e_f1_l, True),
])
fob1 = f.face_outer_bound(loop1)

d_z = f.direction((0.0, 0.0, 1.0))
plc1 = f.axis2_placement_3d(p_00, d_z, d_x)
plane1 = f.plane(plc1)
face1 = f.advanced_face([fob1], plane1, name="face1")

# Second face: adjacent rectangle at x=1, also 1x5
p_20 = f.cartesian_point((2.0, 0.0, 0.0))
p_21 = f.cartesian_point((2.0, 5.0, 0.0))
v_20 = f.vertex_point(p_20)
v_21 = f.vertex_point(p_21)

vx1b = f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)
vy5b = f.vector(f.direction((0.0, 1.0, 0.0)), 5.0)
vnx1b = f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)
vny5b = f.vector(f.direction((0.0, -1.0, 0.0)), 5.0)

e_f2_bot = f.edge_curve(v_10, v_20, f.line(p_10, vx1b))
e_f2_r   = f.edge_curve(v_20, v_21, f.line(p_20, vy5b))
e_f2_top = f.edge_curve(v_21, v_11, f.line(p_21, vnx1b))

loop2 = f.edge_loop([
    f.oriented_edge(e_f2_bot, True),
    f.oriented_edge(e_f2_r, True),
    f.oriented_edge(e_f2_top, True),
    f.oriented_edge(e_f1_r, False),  # shared edge reversed (double-count path)
])
fob2 = f.face_outer_bound(loop2)
plc2 = f.axis2_placement_3d(p_10, d_z, f.direction((1.0, 0.0, 0.0)))
plane2 = f.plane(plc2)
face2 = f.advanced_face([fob2], plane2, name="face2")

shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N082.stp")
