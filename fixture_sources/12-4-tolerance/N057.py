"""N057 — ShapeAnalysis_ShapeTolerance.GlobalTolerance weight dispatch inversion

GlobalTolerance(shape, type, 0=avg) computes weighted average tolerance, but
weight assignment inverts for nested shapes — shell's faces are counted twice,
skewing the average toward face tolerances and violating unbiased averaging
semantics across all geometry types.

Two faces with different tolerances. Average should be (0.001 + 0.008)/2 =
0.0045 but weight inversion skews toward face_2 (0.008).

Byte assertions:
  contains(b'face1_tolerance')
  contains(b'face2_tolerance')
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 3

Tier-3: n_faces_total == 2
Expected: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N057",
    defect=(
        "CLOSED_SHELL with two PLANE faces (face_1 tol=1e-3, face_2 tol=8e-3); "
        "GlobalTolerance weight inversion double-counts shell faces; "
        "two UNCERTAINTY_MEASURE_WITH_UNIT entries (1e-3 + 8e-3) in geometry context"
    ),
)

# Face 1: 1x1 square at z=0, tolerance ~0.001
p1_1 = f.cartesian_point((0.0, 0.0, 0.0), name="p1_1")
p1_2 = f.cartesian_point((1.0, 0.0, 0.0), name="p1_2")
p1_3 = f.cartesian_point((1.0, 1.0, 0.0), name="p1_3")
p1_4 = f.cartesian_point((0.0, 1.0, 0.0), name="p1_4")

v1_1 = f.vertex_point(p1_1, name="v1_1")
v1_2 = f.vertex_point(p1_2, name="v1_2")
v1_3 = f.vertex_point(p1_3, name="v1_3")
v1_4 = f.vertex_point(p1_4, name="v1_4")

d1_1 = f.direction((1.0, 0.0, 0.0), name="d1_1")
vi1_1 = f.vector(d1_1, 1.0, name="v1_1")
l1_1 = f.line(p1_1, vi1_1, name="l1_1")
e1_1 = f.edge_curve(v1_1, v1_2, l1_1, name="e1_1")

d1_2 = f.direction((0.0, 1.0, 0.0), name="d1_2")
vi1_2 = f.vector(d1_2, 1.0, name="v1_2")
l1_2 = f.line(p1_2, vi1_2, name="l1_2")
e1_2 = f.edge_curve(v1_2, v1_3, l1_2, name="e1_2")

d1_3 = f.direction((-1.0, 0.0, 0.0), name="d1_3")
vi1_3 = f.vector(d1_3, 1.0, name="v1_3")
l1_3 = f.line(p1_3, vi1_3, name="l1_3")
e1_3 = f.edge_curve(v1_3, v1_4, l1_3, name="e1_3")

d1_4 = f.direction((0.0, -1.0, 0.0), name="d1_4")
vi1_4 = f.vector(d1_4, 1.0, name="v1_4")
l1_4 = f.line(p1_4, vi1_4, name="l1_4")
e1_4 = f.edge_curve(v1_4, v1_1, l1_4, name="e1_4")

loop1 = f.edge_loop([
    f.oriented_edge(e1_1, True),
    f.oriented_edge(e1_2, True),
    f.oriented_edge(e1_3, True),
    f.oriented_edge(e1_4, True),
])
fob1 = f.face_outer_bound(loop1)
plc1 = f.axis2_placement_3d(p1_1, f.direction((0.0, 0.0, 1.0), name="z1"), f.direction((1.0, 0.0, 0.0), name="x1"), name="ax3_f1")
plane1 = f.plane(plc1, name="plane_f1")
face1 = f.advanced_face([fob1], plane1, name="face_1")

# Face 2: 1x1 square at z=1, tolerance ~0.008 (higher)
p2_1 = f.cartesian_point((0.0, 0.0, 1.0), name="p2_1")
p2_2 = f.cartesian_point((1.0, 0.0, 1.0), name="p2_2")
p2_3 = f.cartesian_point((1.0, 1.0, 1.0), name="p2_3")
p2_4 = f.cartesian_point((0.0, 1.0, 1.0), name="p2_4")

v2_1 = f.vertex_point(p2_1, name="v2_1")
v2_2 = f.vertex_point(p2_2, name="v2_2")
v2_3 = f.vertex_point(p2_3, name="v2_3")
v2_4 = f.vertex_point(p2_4, name="v2_4")

d2_1 = f.direction((1.0, 0.0, 0.0), name="d2_1")
vi2_1 = f.vector(d2_1, 1.0, name="v2_1")
l2_1 = f.line(p2_1, vi2_1, name="l2_1")
e2_1 = f.edge_curve(v2_1, v2_2, l2_1, name="e2_1")

d2_2 = f.direction((0.0, 1.0, 0.0), name="d2_2")
vi2_2 = f.vector(d2_2, 1.0, name="v2_2")
l2_2 = f.line(p2_2, vi2_2, name="l2_2")
e2_2 = f.edge_curve(v2_2, v2_3, l2_2, name="e2_2")

d2_3 = f.direction((-1.0, 0.0, 0.0), name="d2_3")
vi2_3 = f.vector(d2_3, 1.0, name="v2_3")
l2_3 = f.line(p2_3, vi2_3, name="l2_3")
e2_3 = f.edge_curve(v2_3, v2_4, l2_3, name="e2_3")

d2_4 = f.direction((0.0, -1.0, 0.0), name="d2_4")
vi2_4 = f.vector(d2_4, 1.0, name="v2_4")
l2_4 = f.line(p2_4, vi2_4, name="l2_4")
e2_4 = f.edge_curve(v2_4, v2_1, l2_4, name="e2_4")

loop2 = f.edge_loop([
    f.oriented_edge(e2_1, True),
    f.oriented_edge(e2_2, True),
    f.oriented_edge(e2_3, True),
    f.oriented_edge(e2_4, True),
])
fob2 = f.face_outer_bound(loop2)
plc2 = f.axis2_placement_3d(p2_1, f.direction((0.0, 0.0, 1.0), name="z2"), f.direction((1.0, 0.0, 0.0), name="x2"), name="ax3_f2")
plane2 = f.plane(plc2, name="plane_f2")
face2 = f.advanced_face([fob2], plane2, name="face_2")

# Shell containing both faces.
# When GlobalTolerance(shell) called, nested iteration may double-count.
shell = f.closed_shell([face1, face2])

# Two tolerance declarations with different values (the defect key elements)
lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc1 = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},'distance_accuracy_value','face1_tolerance')")
unc2 = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(8.0E-3),#{lu.eid},'distance_accuracy_value','face2_tolerance')")

# Product chain manually (to use the 2-uncertainty context as geometry context)
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N057','N057','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')")
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

# Second context for the product chain (separate from geometry context)
lu2 = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau2 = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau2 = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc_chain = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu2.eid},'distance_accuracy_value','')")
geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_chain.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu2.eid},#{pau2.eid},#{sau2.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)

sbsm = f.shell_based_surface_model([shell], name="sbsm")
shape_rep = f._emit_raw(
    f"MANIFOLD_SURFACE_SHAPE_REPRESENTATION('',(#{sbsm.eid}),#{geom_ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{shape_rep.eid})")

f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N057.stp")
