"""Gp050 — ShapeFix_Edge.FixSameParameter recursive SameRange stack overflow.

Catalog claim: Edge with high-degree B-spline 3D curve (degree 3, 10 control
points, 11-knot vector) paired with a degree-2 PCURVE B-spline (3 control
points). The knot-domain mismatch triggers recursive SameRange refinement; on
deep nesting the recursion consumes stack depth before convergence.

Mechanism: The defect IS in the pcurve — a deg-2 B-spline with only 3 CPs
paired against a 10-CP deg-3 3D curve. The pcurve knot domain [0,1] vs the 3D
curve's knot domain [0,9] creates the mismatch that triggers recursive SameRange.
The pcurve IS wired through PCURVE → SURFACE_CURVE → EDGE_CURVE → face topology.

Tier-3 assertion: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp050",
    defect=(
        "Degree-3 B-spline 3D curve with 10 CPs (knot domain [0,9]) paired with "
        "degree-2 pcurve B-spline with only 3 CPs (knot domain [0,1]); "
        "domain ratio 9:1 triggers FixSameParameter recursive SameRange refinement "
        "that consumes stack depth before convergence; defect IS in pcurve wired "
        "through PCURVE→SURFACE_CURVE→EDGE_CURVE"
    ),
)

# Host surface: planar z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f._emit_raw(f"PLANE('gp050_host',#{plc.eid})")

# 3D curve: degree-3 B-spline, 10 CPs, knot domain [0,9]
# 10 CPs + degree 3 + 1 = 14 entries; mults: (4, 1, 1, 1, 1, 1, 1, 4) = 4+6+4=14 ✓
# Knot vector: (0,1,2,3,4,5,6,9)
cp3d = [
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.cartesian_point((1.0, 0.3, 0.0)),
    f.cartesian_point((2.0, -0.2, 0.0)),
    f.cartesian_point((3.0, 0.4, 0.0)),
    f.cartesian_point((4.0, -0.1, 0.0)),
    f.cartesian_point((5.0, 0.3, 0.0)),
    f.cartesian_point((6.0, -0.2, 0.0)),
    f.cartesian_point((7.0, 0.1, 0.0)),
    f.cartesian_point((8.0, -0.1, 0.0)),
    f.cartesian_point((9.0, 0.0, 0.0)),
]
cp3d_refs = ",".join(f"#{p.eid}" for p in cp3d)
# Endpoint vertices
v_s = f.vertex_point(cp3d[0])
v_e = f.vertex_point(cp3d[-1])

curve_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gp050_3d_deg3_10cp',3,"
    f"({cp3d_refs}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,1,1,1,1,4),(0.0,1.0,2.0,3.0,4.0,5.0,6.0,9.0),.UNSPECIFIED.)"
)

# CATALOG MECHANISM: degree-2 pcurve B-spline with only 3 CPs, domain [0,1]
# The mismatch: 3D domain is [0,9], pcurve domain is [0,1] → 9:1 ratio.
# SameRange recursively subdivides to match; 10-CP vs 3-CP recursion diverges.
uv0 = f.cartesian_point((0.0, 0.0))
uv1 = f.cartesian_point((0.5, 0.0))
uv2 = f.cartesian_point((1.0, 0.0))
pcurve_basis = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gp050_pcurve_deg2_3cp',2,"
    f"(#{uv0.eid},#{uv1.eid},#{uv2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gp050_def',(#{pcurve_basis.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gp050_uv',#{plane.eid},#{defrep.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('gp050_sc',#{curve_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('gp050_edge',#{v_s.eid},#{v_e.eid},#{surface_curve.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
