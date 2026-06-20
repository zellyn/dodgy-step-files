"""Gp061 — ShapeAnalysis_Edge.CheckCurve3dWithPCurve sample-count threshold.

Catalog claim: Very short edge (0.001 units on cylindrical surface) triggers
sample-count collapse to 2, skipping midspan validation between 3D curve and
pcurve. Reproduces OCCT scaling logic that reduces samples below viable
threshold for short edges.

Mechanism: The defect IS in the pcurve bow that 2-sample misses. A 3-CP
degree-2 pcurve B-spline whose middle CP bows off the straight-line path by
0.1 UV units — which a 2-sample check (endpoint-only) completely misses.
The edge is 0.001 units long in 3D (on a cylindrical surface) to trigger the
sample-count collapse to 2 samples. The pcurve IS wired through
PCURVE → SURFACE_CURVE → EDGE_CURVE → face topology.

Tier-3 assertion: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp061",
    defect=(
        "0.001-unit-long edge on CYLINDRICAL_SURFACE (r=1.0); "
        "degree-2 pcurve B-spline with 3 CPs: start=(0,0), mid=(0.0005, 0.1), end=(0.001,0); "
        "midpoint bows 0.1 UV-units off straight path; "
        "CheckCurve3dWithPCurve collapses to 2 samples for short edge → "
        "endpoint-only check misses bow in pcurve; defect IS in pcurve"
    ),
)

# Host surface: unit cylinder, radius=1.0, axis Z
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cylinder = f.cylindrical_surface(cyl_plc, 1.0)

# 0.001-unit edge on the cylinder at u=0, v=0..0.001
# At u=0: 3D point = (cos(0), sin(0), v) = (1, 0, v)
p_s = f.cartesian_point((1.0, 0.0, 0.000))
p_e = f.cartesian_point((1.0, 0.0, 0.001))
v_s = f.vertex_point(p_s)
v_e = f.vertex_point(p_e)

# 3D curve: straight line along Z (length=0.001)
d_z   = f.direction((0.0, 0.0, 1.0))
vec_z = f.vector(d_z, 0.001)
line3d = f.line(p_s, vec_z)

# CATALOG MECHANISM: degree-2 pcurve B-spline with bow at midpoint
# CPs: (0,0), (0.0005, 0.1), (0.001, 0)
# The midpoint bows 0.1 units in V — the 2-sample check (t=0 and t=1)
# only checks endpoints and completely misses this bow.
# Knots: (0, 1) mults (3,3); domain [0,1]
uv0 = f.cartesian_point((0.0000, 0.000))
uv1 = f.cartesian_point((0.0005, 0.100))   # BOW: 0.1 UV units off-path
uv2 = f.cartesian_point((0.0010, 0.000))
pcurve_basis = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gp061_bow_pcurve',2,"
    f"(#{uv0.eid},#{uv1.eid},#{uv2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gp061_def',(#{pcurve_basis.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gp061_uv',#{cylinder.eid},#{defrep.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('gp061_sc',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('gp061_edge',#{v_s.eid},#{v_e.eid},#{surface_curve.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], cylinder)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
