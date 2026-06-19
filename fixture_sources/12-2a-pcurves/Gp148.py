"""Gp148 — GetEndTangent2d falls back to line endpoints (D3-zero pcurve).

Catalog claim: edge pcurve where the local 2D curve has D1=D2=D3=0 at the
endpoint — i.e. complete derivative degeneracy. ShapeAnalysis_Edge::
GetEndTangent2d resorts to linear interpolation between endpoints without
reporting full degeneracy.

A LINE has D1≠0 by definition, so the prior fixture using a LINE pcurve
couldn't represent the claimed D1=D2=D3=0 case. Regen: use a degree-3
B-spline curve whose first four control points (degree+1) all coincide,
which yields all derivatives ≡ 0 in the initial knot span. That's the
exact corner case GetEndTangent2d's escalation chain is supposed to detect.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp148",
             defect="pcurve with D1=D2=D3=0 at start (4 coincident control points)")

# Carrier plane in UV space.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# 2D B-spline curve: degree 3, with 4 coincident control points at (0,0)
# followed by a fifth at (1,0). Because the first 4 = degree+1 poles
# coincide, D0, D1, D2, D3 all evaluate to zero at the start knot.
uv0 = f.cartesian_point((0.0, 0.0))
uv1 = f.cartesian_point((0.0, 0.0))   # coincident
uv2 = f.cartesian_point((0.0, 0.0))   # coincident
uv3 = f.cartesian_point((0.0, 0.0))   # coincident — total 4 stacked
uv4 = f.cartesian_point((1.0, 0.0))
bspline2d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('all_derivs_zero_at_start',3,"
    f"(#{uv0.eid},#{uv1.eid},#{uv2.eid},#{uv3.eid},#{uv4.eid}),"
    ".UNSPECIFIED.,.F.,.F.,"
    "(4,1,4),"
    "(0.0,0.5,1.0),"
    ".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('uv_ctx','UV'))"
)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('uv_def',(#{bspline2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(
    f"PCURVE('pcurve_d3_zero',#{plane.eid},#{defrep.eid})"
)

# 3D edge with the degenerate pcurve.
p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end = f.cartesian_point((1.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end = f.vertex_point(p_end)
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 1.0)
ln = f.line(p_start, vec)
surf_curve = f._emit_raw(
    f"SURFACE_CURVE('edge_with_d3_zero_pcurve',#{ln.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('edge_degen_pcurve',#{v_start.eid},#{v_end.eid},#{surf_curve.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
