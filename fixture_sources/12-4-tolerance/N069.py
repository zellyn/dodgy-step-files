"""N069 — ShapeAnalysis_Edge.CheckOverlapping parameter vs arc-length scale

Overlap detection compares edges by parameter distance, not arc length,
causing false positives when parameter ranges differ in scale. Edge1 domain
[0,1] vs Edge2 domain [0,100] both represent same 1mm geometry; parameter
distance 0.5 is dimensionless. Root cause: tolerance comparison uses parameter
delta without range normalization.

Fixture: two overlapping 1mm lines with parameter domains [0,1] and [0,100].

Byte assertions:
  contains(b'e1')
  contains(b'e2')
  count_entity_def(b'EDGE_CURVE') >= 5

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N069",
    defect=(
        "edge e1 (domain [0,1], vec magnitude=1.0) and edge e2 (domain [0,100], "
        "vec magnitude=0.01) represent same 1mm geometry; CheckOverlapping raw "
        "param delta sees 100x range — false positive without arc-length normalization"
    ),
)

# Edge 1: 1mm line, param domain [0,1] — VECTOR magnitude = 1.0
p_e1_0 = f.cartesian_point((0.0, 0.0, 0.0), name="e1_p0")
p_e1_1 = f.cartesian_point((1.0, 0.0, 0.0), name="e1_p1")
v_e1_0 = f.vertex_point(p_e1_0, name="e1_v0")
v_e1_1 = f.vertex_point(p_e1_1, name="e1_v1")
d1 = f.direction((1.0, 0.0, 0.0), name="d1")
vec1 = f.vector(d1, 1.0, name="vec1")  # magnitude = 1.0, param domain [0,1]
l1 = f.line(p_e1_0, vec1, name="l1")
e1 = f.edge_curve(v_e1_0, v_e1_1, l1, name="e1")

# Edge 2: same 1mm geometry, param domain [0,100] — VECTOR magnitude = 0.01
# (so that 100 param units covers the same 1mm arc length).
# CheckOverlapping using raw param delta sees 100x apparent range.
p_e2_0 = f.cartesian_point((0.0, 0.0, 0.0), name="e2_p0")
p_e2_1 = f.cartesian_point((1.0, 0.0, 0.0), name="e2_p1")
v_e2_0 = f.vertex_point(p_e2_0, name="e2_v0")
v_e2_1 = f.vertex_point(p_e2_1, name="e2_v1")
d2 = f.direction((1.0, 0.0, 0.0), name="d2")
vec2 = f.vector(d2, 0.01, name="vec2")  # magnitude = 0.01, param domain [0,100]
l2 = f.line(p_e2_0, vec2, name="l2")
e2 = f.edge_curve(v_e2_0, v_e2_1, l2, name="e2")

# Face containing e1 via closed loop, with e2 as a reference (overlapping parametrically)
d_y = f.direction((0.0, 1.0, 0.0), name="ydir")
vec_y = f.vector(d_y, 1.0, name="yvec")
l_up = f.line(p_e1_1, vec_y, name="line_up")
p_tr = f.cartesian_point((1.0, 1.0, 0.0), name="pt_tr")
v_tr = f.vertex_point(p_tr, name="v_tr")
e_up = f.edge_curve(v_e1_1, v_tr, l_up, name="e_up")

d_negx = f.direction((-1.0, 0.0, 0.0), name="negx")
vec_negx = f.vector(d_negx, 1.0, name="negxvec")
l_back = f.line(p_tr, vec_negx, name="line_back")
p_tl = f.cartesian_point((0.0, 1.0, 0.0), name="pt_tl")
v_tl = f.vertex_point(p_tl, name="v_tl")
e_back = f.edge_curve(v_tr, v_tl, l_back, name="e_back")

d_negy = f.direction((0.0, -1.0, 0.0), name="negy")
vec_negy = f.vector(d_negy, 1.0, name="negyvec")
l_down = f.line(p_tl, vec_negy, name="line_down")
e_down = f.edge_curve(v_tl, v_e1_0, l_down, name="e_down")

loop = f.edge_loop([
    f.oriented_edge(e1, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_down, True),
])
fob = f.face_outer_bound(loop)

d_z = f.direction((0.0, 0.0, 1.0), name="zdir")
d_x2 = f.direction((1.0, 0.0, 0.0), name="xdir2")
plc = f.axis2_placement_3d(p_e1_0, d_z, d_x2, name="ax3")
plane = f.plane(plc, name="plane")
face = f.advanced_face([fob], plane, name="face")
shell = f.open_shell([face], name="shell")

# Units and loose tolerance
lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-2),#{lu.eid},'distance_accuracy_value','')")
_geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)

sbsm = f.shell_based_surface_model([shell], name="sbsm")
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N069.stp")
