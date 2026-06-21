"""N066 — ShapeAnalysis_ShapeTolerance.OverTolerance >= vs > comparison

OverTolerance comparison operator bug: method uses >= instead of > when
comparing vertex tolerance against threshold, flagging 0.0 tolerance as
exceeding any positive threshold. Root cause: boundary condition equality
treated as over-tolerance state rather than at-threshold state.

Fixture: vertex with 0.0 declared tolerance, global context 1e-3.
OverTolerance(shape, 1e-3) should return false; with bug returns true.

Byte assertions:
  contains(b'zero_vertex_tolerance')
  contains(b'threshold')
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 3

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N066",
    defect=(
        "CLOSED_SHELL 1×1 square face; zero_vertex_tolerance=0.0 and threshold=1e-3 "
        "in geometry context; OverTolerance(shape, 1e-3) with >= operator "
        "misidentifies at-threshold case as over-tolerance"
    ),
)

# Simple 1x1 square face with zero-tolerance vertex v0
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((1.0, 0.0, 0.0), name="p1")
p2 = f.cartesian_point((1.0, 1.0, 0.0), name="p2")
p3 = f.cartesian_point((0.0, 1.0, 0.0), name="p3")

v0 = f.vertex_point(p0, name="v0")  # zero-tolerance vertex
v1 = f.vertex_point(p1, name="v1")
v2 = f.vertex_point(p2, name="v2")
v3 = f.vertex_point(p3, name="v3")

d_x = f.direction((1.0, 0.0, 0.0), name="xdir")
vec_x = f.vector(d_x, 1.0, name="xvec")
l_e0 = f.line(p0, vec_x, name="line")
e0 = f.edge_curve(v0, v1, l_e0, name="e0")

d_y = f.direction((0.0, 1.0, 0.0), name="ydir")
vec_y = f.vector(d_y, 1.0, name="yvec")
l_up = f.line(p1, vec_y, name="line_up")
e_up = f.edge_curve(v1, v2, l_up, name="e_up")

d_negx = f.direction((-1.0, 0.0, 0.0), name="negx")
vec_negx = f.vector(d_negx, 1.0, name="negxvec")
l_back = f.line(p2, vec_negx, name="line_back")
e_back = f.edge_curve(v2, v3, l_back, name="e_back")

d_negy = f.direction((0.0, -1.0, 0.0), name="negy")
vec_negy = f.vector(d_negy, 1.0, name="negyvec")
l_down = f.line(p3, vec_negy, name="line_down")
e_down = f.edge_curve(v3, v0, l_down, name="e_down")

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_down, True),
])
fob = f.face_outer_bound(loop)

d_z = f.direction((0.0, 0.0, 1.0), name="zdir")
d_x2 = f.direction((1.0, 0.0, 0.0), name="xdir2")
plc = f.axis2_placement_3d(p0, d_z, d_x2, name="ax3")
plane = f.plane(plc, name="plane")
face = f.advanced_face([fob], plane, name="face")
shell = f.closed_shell([face], name="shell")

# Units with tolerance context: 1.0e-3 mm as global threshold.
# Vertex v0 has zero-tolerance in a separate declaration.
lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Zero tolerance declaration (the at-threshold vertex)
unc_z = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.0),#{lu.eid},'distance_accuracy_value','zero_vertex_tolerance')")
# Global threshold: 1.0e-3
unc_t = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},'distance_accuracy_value','threshold')")
_geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_z.eid},#{unc_t.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)

sbsm = f.shell_based_surface_model([shell], name="sbsm")
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N066.stp")
