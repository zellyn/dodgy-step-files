"""Gp007 — Edge parameter range outside the pcurve's natural domain.

Catalog claim: An edge's 3D `SURFACE_CURVE` companion declares a parameter
range that lies outside the natural domain of its `PCURVE`. The receiver
evaluating the pcurve at the declared 3D-curve parameter walks off the
end of the pcurve's basis B-spline.

Fixture (rebuilt 2026-06-19 per Sonnet verify): a planar face whose edge
has a SURFACE_CURVE composed of:
  - 3D curve: B-spline with natural domain [0, 2.5] (knot vector reaches
    2.5, so end-parameter evaluation is at 2.5).
  - PCURVE: 2D B-spline with natural domain [0, 1.0] (knot vector ends
    at 1.0).
The edge traverses the 3D curve from param 0 to its end (2.5). A receiver
that evaluates the pcurve at the same parameter (without remapping) walks
off the pcurve's [0,1] basis domain.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp007",
             defect="3D-curve domain [0,2.5] exceeds pcurve basis domain [0,1]")

# Planar host surface (z=0)
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f._emit_raw(f"PLANE('host',#{plc.eid})")

# Vertex endpoints — same physical points, just different parameter coords
# along the 3D vs 2D curve.
p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end_3d = f.cartesian_point((2.5, 0.0, 0.0))   # 3D end at u=2.5
v_start = f.vertex_point(p_start)
v_end = f.vertex_point(p_end_3d)

# 3D curve: degree-1 B-spline with knot vector [0, 0, 2.5, 2.5], domain [0, 2.5].
curve_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('c3d_domain_0_to_2_5',1,"
    f"(#{p_start.eid},#{p_end_3d.eid}),"
    f".POLYLINE_FORM.,.F.,.F.,(2,2),(0.0,2.5),.UNSPECIFIED.)"
)

# 2D pcurve basis: degree-1 B-spline with knot vector [0,0,1,1], domain [0,1].
uv_start = f.cartesian_point((0.0, 0.0))
uv_end = f.cartesian_point((1.0, 0.0))
pcurve_basis = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('pcurve_basis_domain_0_to_1',1,"
    f"(#{uv_start.eid},#{uv_end.eid}),"
    f".POLYLINE_FORM.,.F.,.F.,(2,2),(0.0,1.0),.UNSPECIFIED.)"
)

# Parametric context for the 2D curve
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pcurve_def',(#{pcurve_basis.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('uv_curve',#{plane.eid},#{defrep.eid})")

# SURFACE_CURVE binds the 3D curve (domain [0,2.5]) to the pcurve (domain [0,1]).
# The defect: the 3D curve's parameter range exceeds the pcurve basis domain;
# evaluating the pcurve at param 2.5 walks past the basis knot vector.
surface_curve = f._emit_raw(
    f"SURFACE_CURVE('mismatched_domains',#{curve_3d.eid},"
    f"(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('edge_2_5_long',#{v_start.eid},#{v_end.eid},"
    f"#{surface_curve.eid},.T.)"
)

# PRODUCT chain so the fixture loads as a real shape (oracle-active).
loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
