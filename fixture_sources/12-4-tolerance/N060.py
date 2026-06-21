"""N060 — ShapeFix_Edge.FixSameParameter SameParameterEdge upper-bound

FixSameParameter computes tolerance to synchronize 3D and parametric curves;
when computed tolerance exceeds user ceiling, silently clamps without flagging.
Caller sees "tolerances fixed" but edge is actually incompatible — same-parameter
constraint cannot be achieved at the ceiling value.

Byte assertions:
  contains(b'edge_large_mismatch')
  contains(b'user_ceiling')
  count_entity_def(b'EDGE_CURVE') == 4

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N060",
    defect=(
        "edge_large_mismatch: 3D LINE from (0,0,0) to (10,0,0) with param domain [0,10]; "
        "PCurve domain [0,1] — mismatch factor 10x; required sync tolerance ~5.0, "
        "user ceiling 0.01; FixSameParameter silently clamps without flagging"
    ),
)

# Edge with large parameter domain mismatch between 3D and 2D curves.
# 3D LINE from (0,0,0) to (10,0,0), param domain [0,10].
# PCurve domain [0,1] — mismatch factor of 10x.
# Required sync tolerance ~5.0, user ceiling is 0.01.
p_start = f.cartesian_point((0.0, 0.0, 0.0), name="p_start")
p_end = f.cartesian_point((10.0, 0.0, 0.0), name="p_end")
v_start = f.vertex_point(p_start, name="v_start")
v_end = f.vertex_point(p_end, name="v_end")

# 3D edge: LINE from 0 to 10, param domain [0, 10]
d_x = f.direction((1.0, 0.0, 0.0), name="xdir")
vec_x = f.vector(d_x, 10.0, name="xvec")
l_main = f.line(p_start, vec_x, name="line_3d")
e_main = f.edge_curve(v_start, v_end, l_main, name="edge_large_mismatch")

# Face on XY plane: edge loop for the face
d_y = f.direction((0.0, 1.0, 0.0), name="ydir")
vec_y = f.vector(d_y, 1.0, name="yvec")
l_up = f.line(p_end, vec_y, name="line_up")
p_tr = f.cartesian_point((10.0, 1.0, 0.0), name="pt_top_right")
v_tr = f.vertex_point(p_tr, name="v_top_right")
e_up = f.edge_curve(v_end, v_tr, l_up, name="edge_up")

d_negx = f.direction((-1.0, 0.0, 0.0), name="negx")
vec_negx = f.vector(d_negx, 10.0, name="negxvec")
l_back = f.line(p_tr, vec_negx, name="line_back")
p_tl = f.cartesian_point((0.0, 1.0, 0.0), name="pt_top_left")
v_tl = f.vertex_point(p_tl, name="v_top_left")
e_back = f.edge_curve(v_tr, v_tl, l_back, name="edge_back")

d_negy = f.direction((0.0, -1.0, 0.0), name="negy")
vec_negy = f.vector(d_negy, 1.0, name="negyvec")
l_down = f.line(p_tl, vec_negy, name="line_down")
e_down = f.edge_curve(v_tl, v_start, l_down, name="edge_down")

loop = f.edge_loop([
    f.oriented_edge(e_main, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_down, True),
])
fob = f.face_outer_bound(loop)

d_z = f.direction((0.0, 0.0, 1.0), name="zdir")
d_x2 = f.direction((1.0, 0.0, 0.0), name="xdir2")
plc = f.axis2_placement_3d(p_start, d_z, d_x2, name="ax3_f1")
plane = f.plane(plc, name="plane_z0")
face = f.advanced_face([fob], plane, name="face_1")

shell = f.open_shell([face], name="shell1")

# Tight tolerance context (0.01 mm ceiling) — the defect key element
lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-2),#{lu.eid},'distance_accuracy_value','user_ceiling')")
_geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)

sbsm = f.shell_based_surface_model([shell], name="sbsm")
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N060.stp")
