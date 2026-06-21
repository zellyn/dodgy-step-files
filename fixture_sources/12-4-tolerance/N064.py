"""N064 — ShapeAnalysis_Edge.CheckPoints precision asymmetry

An edge with asymmetric vertex tolerances (preci1 ≠ preci2) is validated by
CheckPoints, which conflates the two precision values into a single tolerance,
losing asymmetry information.

Geometry: Single edge from (0,0,0) to (10,0,0) with coarse endpoint (1e-2)
and fine endpoint (1e-5). Two UNCERTAINTY_MEASURE_WITH_UNIT entries.

Byte assertions:
  contains(b'coarse_vtx')
  contains(b'fine_vtx')
  contains(b'coarse_tolerance')
  contains(b'fine_tolerance')

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N064",
    defect=(
        "CLOSED_SHELL face with asym_edge from coarse_vtx (1e-2) to fine_vtx (1e-5); "
        "two UNCERTAINTY_MEASURE entries coarse_tolerance=1e-2 and fine_tolerance=1e-5; "
        "CheckPoints conflates them into single value, losing asymmetry"
    ),
)

# Edge endpoints with asymmetric precision characteristics
p_coarse = f.cartesian_point((0.0, 0.0, 0.0), name="p_coarse")
p_fine = f.cartesian_point((10.0, 0.0, 0.0), name="p_fine")
v_coarse = f.vertex_point(p_coarse, name="coarse_vtx")
v_fine = f.vertex_point(p_fine, name="fine_vtx")

# Edge curve: LINE from coarse to fine endpoint
d_x = f.direction((1.0, 0.0, 0.0), name="xdir")
vec_x = f.vector(d_x, 10.0, name="xvec")
l_main = f.line(p_coarse, vec_x, name="edge_line")
e_main = f.edge_curve(v_coarse, v_fine, l_main, name="asym_edge")

# Close the loop for valid face
d_y = f.direction((0.0, 1.0, 0.0), name="ydir")
vec_y = f.vector(d_y, 1.0, name="yvec")
l_up = f.line(p_fine, vec_y, name="line_up")
p_tr = f.cartesian_point((10.0, 1.0, 0.0), name="pt_tr")
v_tr = f.vertex_point(p_tr, name="v_tr")
e_up = f.edge_curve(v_fine, v_tr, l_up, name="e_up")

d_negx = f.direction((-1.0, 0.0, 0.0), name="negx")
vec_negx = f.vector(d_negx, 10.0, name="negxvec")
l_back = f.line(p_tr, vec_negx, name="line_back")
p_tl = f.cartesian_point((0.0, 1.0, 0.0), name="pt_tl")
v_tl = f.vertex_point(p_tl, name="v_tl")
e_back = f.edge_curve(v_tr, v_tl, l_back, name="e_back")

d_negy = f.direction((0.0, -1.0, 0.0), name="negy")
vec_negy = f.vector(d_negy, 1.0, name="negyvec")
l_down = f.line(p_tl, vec_negy, name="line_down")
e_down = f.edge_curve(v_tl, v_coarse, l_down, name="e_down")

loop = f.edge_loop([
    f.oriented_edge(e_main, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_down, True),
])
fob = f.face_outer_bound(loop)

d_z = f.direction((0.0, 0.0, 1.0), name="zdir")
d_x2 = f.direction((1.0, 0.0, 0.0), name="xdir2")
plc = f.axis2_placement_3d(p_coarse, d_z, d_x2, name="ax3")
plane = f.plane(plc, name="plane_xy")
face = f.advanced_face([fob], plane, name="face")
shell = f.closed_shell([face], name="shell")

# Asymmetric tolerance declarations — the defect core
lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Coarse endpoint tolerance: 1.0e-2
unc_c = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-2),#{lu.eid},'distance_accuracy_value','coarse_tolerance')")
# Fine endpoint tolerance: 1.0e-5
unc_f = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-5),#{lu.eid},'distance_accuracy_value','fine_tolerance')")
_geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_c.eid},#{unc_f.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)

sbsm = f.shell_based_surface_model([shell], name="sbsm")
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N064.stp")
