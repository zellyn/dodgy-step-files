"""N072 — ShapeFix_Edge.FixSameParameter precision-loss via TempSameRange

TempSameRange clamps parameter range [0, 10] -> [0.5, 9.5] on a B-spline edge.
Original curve has geometric tolerance 1.0E-5 mm. Clamping re-parameterizes
curve to occupy only [0.5, 9.5], shrinking effective resolution: geometric
tolerance relative to range becomes 100x tighter. Precision-loss: tolerance not
adjusted after param clamping, causing silent precision degradation.

Byte assertions:
  contains(b'bspline_wide_param')
  contains(b'e_bspline')
  count_entity_def(b'B_SPLINE_CURVE_WITH_KNOTS') == 1

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(5) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N072",
    defect=(
        "B-spline bspline_wide_param with param range [0, 10] (knots 0.0/5.0/10.0); "
        "TempSameRange clamps to [0.5, 9.5]; tolerance 1e-5 not adjusted after "
        "clamping — silent 100x precision loss in effective resolution"
    ),
)

# B-spline edge with parameter range [0, 10], high precision tolerance 1.0e-5 mm.
# TempSameRange will clamp to [0.5, 9.5], introducing precision loss.
p_start = f.cartesian_point((0.0, 0.0, 0.0), name="p_start")
p_end = f.cartesian_point((10.0, 0.0, 0.0), name="p_end")
v_start = f.vertex_point(p_start, name="v_start")
v_end = f.vertex_point(p_end, name="v_end")

# Interior control points
cp1 = f.cartesian_point((2.5, 1.0, 0.0), name="cp1")
cp2 = f.cartesian_point((5.0, 0.0, 0.0), name="cp2")
cp3 = f.cartesian_point((7.5, 1.0, 0.0), name="cp3")

# B-spline curve with parameter range [0, 10]
bsc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('bspline_wide_param',3,"
    f"(#{p_start.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{p_end.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,4),(0.0,5.0,10.0),"
    f".UNSPECIFIED.)"
)
e_bsp = f.edge_curve(v_start, v_end, bsc, name="e_bspline")

# Close the loop with straight return
d_negx = f.direction((-1.0, 0.0, 0.0), name="negx")
vec_negx = f.vector(d_negx, 10.0, name="negxvec")
l_close = f.line(p_end, vec_negx, name="close_line")
e_close = f.edge_curve(v_end, v_start, l_close, name="close_edge")

loop = f.edge_loop([
    f.oriented_edge(e_bsp, True),
    f.oriented_edge(e_close, True),
])
fob = f.face_outer_bound(loop)

d_z = f.direction((0.0, 0.0, 1.0), name="zdir")
d_x = f.direction((1.0, 0.0, 0.0), name="xdir")
plc = f.axis2_placement_3d(p_start, d_z, d_x, name="ax3")
plane = f.plane(plc, name="plane")
face = f.advanced_face([fob], plane, name="face")
shell = f.open_shell([face], name="shell")

# Units and tight tolerance (1.0E-5 mm)
lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-5),#{lu.eid},'distance_accuracy_value','')")
_geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)

sbsm = f.shell_based_surface_model([shell], name="sbsm")
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N072.stp")
