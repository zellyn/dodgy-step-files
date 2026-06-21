"""N122 — ShapeAnalysis_Edge.CheckPoints with-NaN-precision-input

CheckPoints called with NaN as precision parameter; the algorithm doesn't
validate and propagates NaN through comparisons (dist > NaN evaluates false
when precision is NaN), skipping point validation.

Input pattern: edge with parametric sample points; precision parameter
initialized to 0.0 (causing NaN-equivalent behavior in distance comparisons).

Byte assertions:
  contains(b'curved_edge')
  contains(b'test_face')

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N122",
    defect=(
        "CLOSED_SHELL test_shell with test_face containing curved_edge on PARABOLA; "
        "UNCERTAINTY_MEASURE set to 0.0 (NaN-equivalent precision); CheckPoints "
        "dist > NaN comparisons always false, skipping all point validation"
    ),
)

# Parabolic curve geometry — points on a parabola opening upward
p0 = f.cartesian_point((0.0, 0.0, 0.0))   # v0 start
p1 = f.cartesian_point((3.0, 4.0, 0.0))   # apex mid
p2 = f.cartesian_point((6.0, 0.0, 0.0))   # v1 end

v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p2, name="v1")

# Parabola: focal distance 2.0, axis through (3,4,0)
p_apex = f.cartesian_point((3.0, 4.0, 0.0))
d_par_z = f.direction((0.0, 0.0, -1.0))
d_par_x = f.direction((-1.0, 0.0, 0.0))
plc_par = f.axis2_placement_3d(p_apex, d_par_z, d_par_x)
parabola = f._emit_raw(f"PARABOLA('curve',#{plc_par.eid},2.0)")

e_curved = f.edge_curve(v0, v1, parabola, name="curved_edge")

# Host surface (plane slightly behind the parabola)
p_surf = f.cartesian_point((0.0, 0.0, -1.0))
d_sz = f.direction((0.0, 0.0, 1.0))
d_sx = f.direction((1.0, 0.0, 0.0))
plc_surf = f.axis2_placement_3d(p_surf, d_sz, d_sx)
host_plane = f.plane(plc_surf)

loop = f.edge_loop([
    f.oriented_edge(e_curved, True),
], name="boundary")
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], host_plane, name="test_face")

shell = f.closed_shell([face], name="test_shell")
sbsm = f.shell_based_surface_model([shell])

# NaN-precision context: UNCERTAINTY_MEASURE = 0.0 (NaN-equivalent)
# Use _emit_raw for the special 0.0 uncertainty (builder clamps to 1e-7)
lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
nan_unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.0),#{lu.eid},"
    "'distance_accuracy_value','nan_precision')"
)
geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{nan_unc.eid}))"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{nan_unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('nan_edge_check','3D'))"
)

# Product chain with standard tolerance
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N122.stp")
