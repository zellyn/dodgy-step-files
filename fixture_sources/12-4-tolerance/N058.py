"""N058 — BRepLib.SameRange null-pcurve null-check dereference

SameRange rescales PCurve domains to match 3D edge parameter range, but
assumes the PCurve exists. When an edge has a null 2D curve on a face
(parametric curve extraction failed), SameRange dereferences the null pointer
without check, masking the failure and corrupting downstream edge state.

Reproducer: ADVANCED_FACE on XY plane with valid edge loop but no PCURVE entity.
SameRange called on this face finds null PCurve for the main edge and
dereferences it.

Byte assertions:
  contains(b'edge_with_null_pcurve')
  contains(b'face_no_pcurve')
  count_entity_def(b'EDGE_CURVE') == 4

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N058",
    defect=(
        "ADVANCED_FACE on PLANE z=0 with no PCURVE entities; "
        "SameRange assumes PCurve exists and dereferences null pointer for "
        "edge_with_null_pcurve, corrupting downstream edge state"
    ),
)

# Edge with parametric domain [0, 10]
p_origin = f.cartesian_point((0.0, 0.0, 0.0), name="origin")
p_end = f.cartesian_point((10.0, 0.0, 0.0), name="end_pt")
v_start = f.vertex_point(p_origin, name="v_start")
v_end = f.vertex_point(p_end, name="v_end")

# 3D edge curve: LINE from origin to end_pt
d_x = f.direction((1.0, 0.0, 0.0), name="xdir")
vec_x = f.vector(d_x, 10.0, name="xvec")
l_main = f.line(p_origin, vec_x, name="edge_3d")
e_main = f.edge_curve(v_start, v_end, l_main, name="edge_with_null_pcurve")

# Face on XY plane: valid edge loop with no PCurve record.
d_z = f.direction((0.0, 0.0, 1.0), name="zdir")
d_x2 = f.direction((1.0, 0.0, 0.0), name="xdir2")
plc = f.axis2_placement_3d(p_origin, d_z, d_x2, name="ax3_f1")
plane = f.plane(plc, name="plane_z0")

# Closing edges to form a valid loop: go around and return
p_return = f.cartesian_point((10.0, 1.0, 0.0), name="pt_return")
v_return = f.vertex_point(p_return, name="v_return")
d_y = f.direction((0.0, 1.0, 0.0), name="ydir")
vec_y = f.vector(d_y, 1.0, name="yvec")
l_up = f.line(p_end, vec_y, name="line_up")
e_up = f.edge_curve(v_end, v_return, l_up, name="edge_up")

d_negx = f.direction((-1.0, 0.0, 0.0), name="negx")
vec_negx = f.vector(d_negx, 10.0, name="negxvec")
p_left = f.cartesian_point((0.0, 1.0, 0.0), name="pt_left")
v_left = f.vertex_point(p_left, name="v_left")
l_back = f.line(p_return, vec_negx, name="line_back")
e_back = f.edge_curve(v_return, v_left, l_back, name="edge_back")

d_negy = f.direction((0.0, -1.0, 0.0), name="negy")
vec_negy = f.vector(d_negy, 1.0, name="negyvec")
l_down = f.line(p_left, vec_negy, name="line_down")
e_down = f.edge_curve(v_left, v_start, l_down, name="edge_down")

loop = f.edge_loop([
    f.oriented_edge(e_main, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_down, True),
])
fob = f.face_outer_bound(loop)
# ADVANCED_FACE with no PCURVE child — SameRange finds null pcurve for the edge
face = f.advanced_face([fob], plane, name="face_no_pcurve")

shell = f.open_shell([face], name="shell1")
sbsm = f.shell_based_surface_model([shell], name="sbsm")
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N058.stp")
