"""N068 — BRepLib.UpdateInnerTolerances minimal 2-point sampling

UpdateInnerTolerances edge-tolerance computation samples B-spline at endpoints
only (2 samples), missing interior curvature. Deviation at mid-curve peak not
captured in tolerance estimate.

Fixture: 4-control-point B-spline with ~5-unit bulge at center, parameterized
[0,1], global context 1.0e-4. Endpoint sampling misses interior curvature
requiring ~1.0e-2 tolerance.

Byte assertions:
  contains(b'bspline_bulge')
  contains(b'bspl_edge')
  count_entity_def(b'B_SPLINE_CURVE_WITH_KNOTS') == 1

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(5) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N068",
    defect=(
        "B-spline bspline_bulge with 4 control points and ~5-unit interior bulge; "
        "UpdateInnerTolerances samples at endpoints only (2 samples), missing "
        "the ~1e-2 peak curvature deviation at center"
    ),
)

# B-spline endpoints
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p3 = f.cartesian_point((10.0, 0.0, 0.0), name="p3")
# Interior control points creating 5-unit bulge
p1 = f.cartesian_point((3.0, 5.0, 0.0), name="p1")
p2 = f.cartesian_point((7.0, 5.0, 0.0), name="p2")

v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p3, name="v1")

# B-spline curve with high interior curvature
bsc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('bspline_bulge',3,"
    f"(#{p0.eid},#{p1.eid},#{p2.eid},#{p3.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,4),(0.0,1.0),"
    f".UNSPECIFIED.)"
)
e_bsp = f.edge_curve(v0, v1, bsc, name="bspl_edge")

# Close the loop with a straight edge
d_negx = f.direction((-1.0, 0.0, 0.0), name="negx")
vec_negx = f.vector(d_negx, 10.0, name="negxvec")
l_close = f.line(p3, vec_negx, name="close_line")
e_close = f.edge_curve(v1, v0, l_close, name="close_edge")

loop = f.edge_loop([
    f.oriented_edge(e_bsp, True),
    f.oriented_edge(e_close, True),
])
fob = f.face_outer_bound(loop)

d_z = f.direction((0.0, 0.0, 1.0), name="zdir")
d_x = f.direction((1.0, 0.0, 0.0), name="xdir")
plc = f.axis2_placement_3d(p0, d_z, d_x, name="ax3")
plane = f.plane(plc, name="plane_xy")
face = f.advanced_face([fob], plane, name="face")

shell = f.open_shell([face], name="shell")

# Units and tight tolerance (1.0E-4 mm) — endpoint sampling misses 1e-2 peak
lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-4),#{lu.eid},'distance_accuracy_value','')")
_geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)

sbsm = f.shell_based_surface_model([shell], name="sbsm")
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N068.stp")
