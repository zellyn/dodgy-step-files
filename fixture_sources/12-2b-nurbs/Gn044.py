"""Gn044 — ShapeUpgrade_ConvertCurve2dToBezier degree-1 skip on degree=1.

Catalog claim: 2D B-spline curve of degree 1 with 3 control points. Degree-
elevation logic should elevate to degree 3 before Bezier extraction but skips
this step when input degree equals 1, causing downstream conversion failures.

Mechanism: the degree-1 2D B-spline IS the pcurve of the face's defect edge,
wired through PCURVE → SURFACE_CURVE → EDGE_CURVE → face's EDGE_LOOP.

Tier-3 assertion: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn044",
    defect=(
        "Degree-1 2D B_SPLINE_CURVE_WITH_KNOTS (3 CPs, knots [0,0,1,2,2] mults [2,1,2]) "
        "IS the pcurve of the face defect edge via PCURVE→SURFACE_CURVE→EDGE_CURVE; "
        "ConvertCurve2dToBezier degree-elevation skips degree=1 input, "
        "causing downstream Bezier extraction failure → empty"
    ),
)

# Host surface: planar z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f._emit_raw(f"PLANE('gn044_host',#{plc.eid})")

# 3D curve: straight line along X from 0 to 2
p3d_s = f.cartesian_point((0.0, 0.0, 0.0))
p3d_e = f.cartesian_point((2.0, 0.0, 0.0))
v3d_s = f.vertex_point(p3d_s)
v3d_e = f.vertex_point(p3d_e)
d3d   = f.direction((1.0, 0.0, 0.0))
vec3d = f.vector(d3d, 2.0)
line3d = f.line(p3d_s, vec3d)

# CATALOG MECHANISM: degree-1 2D B-spline pcurve with 3 CPs
# Knots [0, 1, 2] mults [2,1,2] → sum=5=3+1+1 ✓; domain [0,2]
# This IS the pcurve that triggers ConvertCurve2dToBezier degree-1 skip.
uv0 = f.cartesian_point((0.0, 0.0))
uv1 = f.cartesian_point((1.0, 0.0))
uv2 = f.cartesian_point((2.0, 0.0))
pcurve_basis = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn044_deg1_pcurve',1,"
    f"(#{uv0.eid},#{uv1.eid},#{uv2.eid}),"
    f".POLYLINE_FORM.,.F.,.F.,(2,1,2),(0.0,1.0,2.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn044_def',(#{pcurve_basis.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn044_uv',#{plane.eid},#{defrep.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('gn044_sc',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('gn044_edge',#{v3d_s.eid},#{v3d_e.eid},#{surface_curve.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
