"""Gp007 — Edge parameter range outside the pcurve's natural domain.

Catalog claim: An edge declares a [first, last] parameter range that lies
outside the natural domain of its pcurve. The receiver evaluating the pcurve
at the declared parameter values walks off the end of the curve definition.

Fixture: A planar face with an edge whose EDGE_CURVE parameter range is
[0, 2.5], but the underlying TRIMMED_CURVE has a pcurve basis with domain
[0, 1]. The trim parameters [1.0, 2.5] lie outside the basis domain.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp007",
             defect="edge parameter range outside pcurve domain")

# Planar surface (z=0)
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f._emit_raw(f"PLANE('',#{plc.eid})")

# 3D curve: B-spline from (0,0,0) to (1,0,0) with natural domain [0,1]
p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end = f.cartesian_point((1.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end = f.vertex_point(p_end)

# 3D B-spline curve with knots (2,2) and domain [0,1]
line3d = f._emit_raw(
    "B_SPLINE_CURVE_WITH_KNOTS('',1,(#1_p_start,#1_p_end),.POLYLINE_FORM.,.F.,.F.,"
    "(2,2),(0.0,1.0),.UNSPECIFIED.)"
)
line3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('',1,(#{p_start.eid},#{p_end.eid}),.POLYLINE_FORM.,.F.,.F.,"
    "(2,2),(0.0,1.0),.UNSPECIFIED.)"
)

# 2D pcurve basis: B-spline from (0,0) to (1,0) with natural domain [0,1]
uv_start = f.cartesian_point((0.0, 0.0))
uv_end = f.cartesian_point((1.0, 0.0))
line2d_basis = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('',1,(#{uv_start.eid},#{uv_end.eid}),.POLYLINE_FORM.,.F.,.F.,"
    "(2,2),(0.0,1.0),.UNSPECIFIED.)"
)

# DEFECT: TRIMMED_CURVE wraps the pcurve basis with trim parameters [0.0, 2.5]
# The basis domain is [0.0, 1.0], so trim_2=2.5 lies OUTSIDE, causing evaluation errors
pval_0 = f._emit_raw("PARAMETER_VALUE(0.0)")
pval_2_5 = f._emit_raw("PARAMETER_VALUE(2.5)")
trimmed_pcurve = f._emit_raw(
    f"TRIMMED_CURVE('',#{line2d_basis.eid},(#{pval_0.eid}),(#{pval_2_5.eid}),.T.,.PARAMETER.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('','2D'))"
)
defrep = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{trimmed_pcurve.eid}),#{prc.eid})")
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
