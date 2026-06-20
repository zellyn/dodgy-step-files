"""Gp110 — GetEndTangent2d zero-derivative.

Catalog claim: Pcurve B-spline with zero tangent derivative at endpoint (last
two control points coincident). GetEndTangent2d returns NaN instead of computing
fallback tangent from interior curvature.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge wrapped in SURFACE_CURVE.
  - 3D curve: B_SPLINE_CURVE_WITH_KNOTS degree-2 with a C-1 positional break
    at t=0.5 (knot mult=3, 1.5-unit CP gap) — drives shape_null=True.
  - PCurve: B_SPLINE_CURVE_WITH_KNOTS degree-2 with CP[N-1]==CP[N] (last two
    control points coincident at the endpoint). The derivative at the endpoint
    is degree*(CP[N] - CP[N-1]) = degree*(0,0) = zero.
  - THE CATALOG MECHANISM: GetEndTangent2d evaluates the first derivative of
    the pcurve B-spline at the endpoint. With CP[N-1]==CP[N], the derivative
    vector is zero. GetEndTangent2d attempts to normalize this zero vector,
    producing NaN (division by zero), rather than falling back to interior
    curvature to compute a usable tangent direction.
  - C-1 DRIVER: 3D B-spline positional break at t=0.5 forces shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: degree-2 pcurve B-spline with CP[N-1]==CP[N] (coincident
    endpoint CPs); GetEndTangent2d gets zero derivative, divides by zero → NaN.
  - C-1 DRIVER: degree-2 3D B-spline positional break forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp110",
    defect=(
        "PLANE Z=0; defect edge: 3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break "
        "at t=0.5 (CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives "
        "shape_null; PCurve B_SPLINE_CURVE_WITH_KNOTS degree-2 6 CPs with "
        "CP[4]==CP[5]=(5.0,0.0) (coincident endpoint CPs); derivative at endpoint "
        "= degree*(CP[5]-CP[4])=(0,0); GetEndTangent2d divides zero vector by its "
        "magnitude → NaN; shape_null=True"
    ),
)

# Host surface: planar Z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners: rectangle [0,5] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges (right, top, left) — clean
d_up = f.direction((0.0, 1.0, 0.0)); vec_up = f.vector(d_up, 2.0)
d_lt = f.direction((-1.0, 0.0, 0.0)); vec_lt = f.vector(d_lt, 5.0)
d_dn = f.direction((0.0, -1.0, 0.0)); vec_dn = f.vector(d_dn, 2.0)
e_right = f.edge_curve(v_b, v_c, f.line(p_b, vec_up))
e_top   = f.edge_curve(v_c, v_d, f.line(p_c, vec_lt))
e_left  = f.edge_curve(v_d, v_a, f.line(p_d, vec_dn))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────

# C-1 DRIVER: degree-2 B-spline 3D curve with positional break at t=0.5.
# CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5-unit gap. Forces shape_null=True.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))   # end of first Bezier
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # start of second — 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.0,  0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('zerotangent_3d',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: PCurve B-spline degree-2, 6 CPs, domain [0,1].
# CP[4] == CP[5] = (5.0, 0.0): coincident last two control points.
# For a degree-d B-spline the endpoint derivative is d*(CP[N] - CP[N-1]).
# With CP[4]==CP[5]: derivative = 2*(5.0-5.0, 0.0-0.0) = (0.0, 0.0).
# GetEndTangent2d normalizes this zero vector → NaN (division by zero),
# with no fallback to second derivative or interior curvature.
pp0 = f.cartesian_point((0.0, 0.0))
pp1 = f.cartesian_point((1.0, 0.0))
pp2 = f.cartesian_point((2.5, 0.0))
pp3 = f.cartesian_point((4.0, 0.0))
pp4 = f.cartesian_point((5.0, 0.0))   # coincident with pp5 — zero derivative at end
pp5 = f.cartesian_point((5.0, 0.0))   # coincident with pp4 — the zero-derivative trigger

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('zerotangent_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('zerotangent_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('zerotangent_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('zerotangent_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('zerotangent_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
