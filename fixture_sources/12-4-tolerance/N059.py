"""N059 — BRepLib.UpdateEdgeTol sampling-grid undersample

UpdateEdgeTol uses 23-sample default grid to detect maximum distance between
3D curve and 2D parametric curve. On B-spline edges with high-curvature peaks
between sample points, the peak distance is never observed, causing
underestimated edge tolerance that fails later validation.

Byte assertions:
  contains(b'bspline_high_curvature')
  contains(b'face_on_plane')
  count_entity_def(b'B_SPLINE_CURVE_WITH_KNOTS') == 1

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(5) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N059",
    defect=(
        "B-spline edge bspline_high_curvature with degree-3 cubic and 5 control "
        "points; peak curvature near u=0.48 falls between 23 default samples; "
        "UpdateEdgeTol underestimates maximum 3D-vs-2D curve deviation"
    ),
)

# B-spline edge with high curvature between sample points.
# 5 control points produce a curve with peak curvature near parameter 0.5.
# With 23 default samples, peak at ~0.48 falls between samples.
cp0 = f.cartesian_point((0.0, 0.0, 0.0), name="cp0")
cp1 = f.cartesian_point((1.0, 0.0, 0.0), name="cp1")
cp2 = f.cartesian_point((2.0, 1.0, 0.0), name="cp2")
cp3 = f.cartesian_point((3.0, 0.5, 0.0), name="cp3")
cp4 = f.cartesian_point((4.0, 0.0, 0.0), name="cp4")

v_start = f.vertex_point(cp0, name="v_start")
v_end = f.vertex_point(cp4, name="v_end")

# B-spline curve degree 3, 5 control points
bsc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('bspline_high_curvature',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,4),(0.0,0.5,1.0),"
    f".UNSPECIFIED.)"
)
e_bsp = f.edge_curve(v_start, v_end, bsc, name="bspline_edge")

# Close the loop with a straight edge returning to start
d_negx = f.direction((-1.0, 0.0, 0.0), name="negx")
vec_negx = f.vector(d_negx, 4.0, name="negxvec")
l_close = f.line(cp4, vec_negx, name="close_line")
e_close = f.edge_curve(v_end, v_start, l_close, name="close_edge")

loop = f.edge_loop([
    f.oriented_edge(e_bsp, True),
    f.oriented_edge(e_close, True),
])
fob = f.face_outer_bound(loop)

# Plane on XY
d_z = f.direction((0.0, 0.0, 1.0), name="zdir")
d_x = f.direction((1.0, 0.0, 0.0), name="xdir")
plc = f.axis2_placement_3d(cp0, d_z, d_x, name="ax3")
plane = f.plane(plc, name="plane_xy")
face = f.advanced_face([fob], plane, name="face_on_plane")

shell = f.open_shell([face], name="shell1")
sbsm = f.shell_based_surface_model([shell], name="sbsm")
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N059.stp")
