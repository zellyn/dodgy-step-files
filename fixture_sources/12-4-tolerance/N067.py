"""N067 — ShapeFix_ShapeTolerance.SetTolerance compound cascade incomplete

SetTolerance recursion stops at shell boundary: compound→shell descent succeeds,
but faces within the shell remain unmodified. Tolerance propagation violates
transitivity contract. Root cause: sub-shape iteration halts at first
boundary-type mismatch rather than continuing depth-first.

Fixture: two-face shell inside compound with initial tolerance 0.1;
SetTolerance(compound, 0.001) leaves face tolerance unchanged.

Byte assertions:
  contains(b'face1')
  contains(b'face2')
  contains(b'two_face_shell')

Tier-3: n_faces_total == 2
Expected: occt=shape(1)/shape(1) gmsh=shape(14) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N067",
    defect=(
        "OPEN_SHELL two_face_shell with face1 and face2 (equilateral triangles); "
        "initial tolerance 0.1 mm in geometry context; SetTolerance(compound, 0.001) "
        "stops at shell boundary — faces remain at 0.1 mm"
    ),
)

# Face 1: equilateral triangle at origin
p1_0 = f.cartesian_point((0.0, 0.0, 0.0), name="f1_p0")
p1_1 = f.cartesian_point((1.0, 0.0, 0.0), name="f1_p1")
p1_2 = f.cartesian_point((0.5, 0.866, 0.0), name="f1_p2")

v1_0 = f.vertex_point(p1_0, name="f1_v0")
v1_1 = f.vertex_point(p1_1, name="f1_v1")
v1_2 = f.vertex_point(p1_2, name="f1_v2")

d1_0 = f.direction((1.0, 0.0, 0.0), name="f1_d0")
vec1_0 = f.vector(d1_0, 1.0, name="f1_vec0")
l1_0 = f.line(p1_0, vec1_0, name="f1_line0")
e1_0 = f.edge_curve(v1_0, v1_1, l1_0, name="f1_e0")

d1_1 = f.direction((-0.5, 0.866, 0.0), name="f1_d1")
vec1_1 = f.vector(d1_1, 1.0, name="f1_vec1")
l1_1 = f.line(p1_1, vec1_1, name="f1_line1")
e1_1 = f.edge_curve(v1_1, v1_2, l1_1, name="f1_e1")

d1_2 = f.direction((-0.5, -0.866, 0.0), name="f1_d2")
vec1_2 = f.vector(d1_2, 1.0, name="f1_vec2")
l1_2 = f.line(p1_2, vec1_2, name="f1_line2")
e1_2 = f.edge_curve(v1_2, v1_0, l1_2, name="f1_e2")

loop1 = f.edge_loop([
    f.oriented_edge(e1_0, True),
    f.oriented_edge(e1_1, True),
    f.oriented_edge(e1_2, True),
])
fob1 = f.face_outer_bound(loop1)

d1_z = f.direction((0.0, 0.0, 1.0), name="f1_z")
d1_x = f.direction((1.0, 0.0, 0.0), name="f1_x")
plc1 = f.axis2_placement_3d(p1_0, d1_z, d1_x, name="f1_ax3")
plane1 = f.plane(plc1, name="f1_plane")
face1 = f.advanced_face([fob1], plane1, name="face1")

# Face 2: triangle shifted to (2,0,0)
p2_0 = f.cartesian_point((2.0, 0.0, 0.0), name="f2_p0")
p2_1 = f.cartesian_point((3.0, 0.0, 0.0), name="f2_p1")
p2_2 = f.cartesian_point((2.5, 0.866, 0.0), name="f2_p2")

v2_0 = f.vertex_point(p2_0, name="f2_v0")
v2_1 = f.vertex_point(p2_1, name="f2_v1")
v2_2 = f.vertex_point(p2_2, name="f2_v2")

d2_0 = f.direction((1.0, 0.0, 0.0), name="f2_d0")
vec2_0 = f.vector(d2_0, 1.0, name="f2_vec0")
l2_0 = f.line(p2_0, vec2_0, name="f2_line0")
e2_0 = f.edge_curve(v2_0, v2_1, l2_0, name="f2_e0")

d2_1 = f.direction((-0.5, 0.866, 0.0), name="f2_d1")
vec2_1 = f.vector(d2_1, 1.0, name="f2_vec1")
l2_1 = f.line(p2_1, vec2_1, name="f2_line1")
e2_1 = f.edge_curve(v2_1, v2_2, l2_1, name="f2_e1")

d2_2 = f.direction((-0.5, -0.866, 0.0), name="f2_d2")
vec2_2 = f.vector(d2_2, 1.0, name="f2_vec2")
l2_2 = f.line(p2_2, vec2_2, name="f2_line2")
e2_2 = f.edge_curve(v2_2, v2_0, l2_2, name="f2_e2")

loop2 = f.edge_loop([
    f.oriented_edge(e2_0, True),
    f.oriented_edge(e2_1, True),
    f.oriented_edge(e2_2, True),
])
fob2 = f.face_outer_bound(loop2)

d2_z = f.direction((0.0, 0.0, 1.0), name="f2_z")
d2_x = f.direction((1.0, 0.0, 0.0), name="f2_x")
plc2 = f.axis2_placement_3d(p2_0, d2_z, d2_x, name="f2_ax3")
plane2 = f.plane(plc2, name="f2_plane")
face2 = f.advanced_face([fob2], plane2, name="face2")

# Shell containing both faces: initial tolerance 0.1 mm
shell = f.open_shell([face1, face2], name="two_face_shell")

# Units and initial high tolerance (0.1 mm)
lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-1),#{lu.eid},'distance_accuracy_value','')")
_geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)

sbsm = f.shell_based_surface_model([shell], name="sbsm")
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N067.stp")
