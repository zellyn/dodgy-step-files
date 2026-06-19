"""Gp008 — Pcurve oscillations producing wire-intersector corruption.

Catalog claim: A pcurve produced by projecting a 3D curve onto a host
surface oscillates at high frequency; the projector lacks adaptive
sampling. A subsequent wire self-intersection check mis-detects the
oscillations as crossings and corrupts wire topology.

Fixture: Planar surface with an edge whose 2D B-spline pcurve control
polygon oscillates wildly in the V direction (high-frequency up/down
motion). The control points produce many zero-crossings of curvature,
triggering spurious self-intersection detection.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp008",
             defect="pcurve oscillations producing wire-intersector corruption")

# Planar surface (z=0)
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f._emit_raw(f"PLANE('',#{plc.eid})")

# 3D curve: smooth line from (0,0,0) to (1,0,0)
p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end = f.cartesian_point((1.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end = f.vertex_point(p_end)

line3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('',1,(#{p_start.eid},#{p_end.eid}),.POLYLINE_FORM.,.F.,.F.,"
    "(2,2),(0.0,1.0),.UNSPECIFIED.)"
)

# DEFECT: 2D B-spline pcurve with high-frequency oscillating control polygon
# Endpoints at (0,0) and (1,0), but interior control points ride up/down
# producing many curvature reversals that trigger false self-intersection detection
uv_cpts = [
    f.cartesian_point((0.0, 0.0)),      # 0: start
    f.cartesian_point((0.1, 0.05)),     # 1: up
    f.cartesian_point((0.2, -0.05)),    # 2: down
    f.cartesian_point((0.3, 0.05)),     # 3: up
    f.cartesian_point((0.4, -0.05)),    # 4: down
    f.cartesian_point((0.5, 0.05)),     # 5: up
    f.cartesian_point((0.6, -0.05)),    # 6: down
    f.cartesian_point((0.7, 0.05)),     # 7: up
    f.cartesian_point((0.8, -0.05)),    # 8: down
    f.cartesian_point((0.9, 0.05)),     # 9: up
    f.cartesian_point((1.0, 0.0)),      # 10: end
]

# Cubic B-spline with 11 control points and appropriate knot vector
# Degree 3, knots: (4,1,1,1,1,1,1,1,4) spanning [0,1]
line2d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('',3,"
    f"({','.join(f'#{pt.eid}' for pt in uv_cpts)}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,1,1,1,1,1,4),"
    f"(0.0,0.125,0.25,0.375,0.5,0.625,0.75,0.875,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('','2D'))"
)
defrep = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{line2d.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('',#{plane.eid},#{defrep.eid})")
surface_curve = f._emit_raw(
    f"SURFACE_CURVE('',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_start.eid},#{v_end.eid},#{surface_curve.eid},.T.)"
)

# Build the face and shell for the PRODUCT chain
loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
