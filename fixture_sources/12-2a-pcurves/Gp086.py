"""Gp086 -- CheckPCurveRange domain-larger-than-3D.

Catalog claim: Edge with B-spline 3D curve spanning [0,5] but B-spline pcurve
spanning [0,10]. CheckPCurveRange validates pcurve range against basis curve
bounds; this fixture exposes out-of-bounds pcurve parameter range. Defect:
analyzer fails to flag domain overspanning on non-periodic curves.

STEP mechanism (literal):
  - PLANE face. The defect edge has:
      3D curve: B_SPLINE_CURVE_WITH_KNOTS, knot vector [0.0, 2.5, 5.0]
        (spans [0, 5]). Degree 2, 6 CPs. Also has a C-1 positional break
        at t=2.5 (knot mult=3) to drive OCC shape_null=True.
      PCurve: B_SPLINE_CURVE_WITH_KNOTS in UV space, knot vector [0.0, 5.0, 10.0]
        (spans [0, 10]). Same degree 2, 6 CPs, smooth.
  - THE DEFECT: the pcurve's parameter domain [0, 10] is 2× larger than the
    3D curve's domain [0, 5]. CheckPCurveRange should flag the overspanning
    (pcurve extends to t=10 while 3D curve only reaches t=5), but the analyzer
    fails to detect this mismatch on non-periodic curves.
  - Both curves are raw B_SPLINE_CURVE_WITH_KNOTS entities (no wrapping), so
    the domain mismatch is directly visible at the STEP entity level.

Mechanism vs driver:
  - CATALOG MECHANISM: B-spline 3D knot domain [0,5] vs B-spline PCurve knot
    domain [0,10] — explicit domain overspanning in the raw STEP knot vectors.
  - C-1 DRIVER: 3D B-spline positional break at t=2.5 forces OCC shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp086",
    defect=(
        "PLANE Z=0; defect edge: 3D B-spline knot domain [0,5] with C-1 break "
        "at t=2.5 (1.5-unit Y gap); PCurve B-spline knot domain [0,10] — 2× "
        "overspanning; CheckPCurveRange fails to flag non-periodic domain "
        "mismatch; C-1 break in 3D curve drives shape_null=True"
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

# Face corners
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges (right, top, left)
d_up = f.direction((0.0, 1.0, 0.0)); vec_up = f.vector(d_up, 2.0)
d_lt = f.direction((-1.0, 0.0, 0.0)); vec_lt = f.vector(d_lt, 5.0)
d_dn = f.direction((0.0, -1.0, 0.0)); vec_dn = f.vector(d_dn, 2.0)
e_right = f.edge_curve(v_b, v_c, f.line(p_b, vec_up))
e_top   = f.edge_curve(v_c, v_d, f.line(p_c, vec_lt))
e_left  = f.edge_curve(v_d, v_a, f.line(p_d, vec_dn))

# ── DEFECT EDGE — bottom (v_a -> v_b) ────────────────────────────────────────

# THE CATALOG MECHANISM PART 1:
# 3D B-spline: knot vector (3,3,3) at (0.0, 2.5, 5.0) → domain [0, 5].
# C-1 positional break at t=2.5: CP[2]=(2.5,0,0) vs CP[3]=(2.5,1.5,0)
# (1.5-unit Y gap at the break point, forcing shape_null).
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((1.0, 0.0, 0.0))
dc2 = f.cartesian_point((2.5, 0.0, 0.0))   # endpoint of first Bezier segment
dc3 = f.cartesian_point((2.5, 1.5, 0.0))   # start of second segment: 1.5Y gap
dc4 = f.cartesian_point((4.0, 0.0, 0.0))
dc5 = f.cartesian_point((5.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('range_3d',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,2.5,5.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM PART 2:
# PCurve B-spline: knot vector (3,3,3) at (0.0, 5.0, 10.0) → domain [0, 10].
# Domain is 2× the 3D curve domain [0, 5] — explicit overspanning.
# PCurve CPs: smooth path in UV from (0,0) to (5,0) (matching the face bottom).
pc0 = f.cartesian_point((0.0, 0.0))
pc1 = f.cartesian_point((1.5, 0.0))
pc2 = f.cartesian_point((2.5, 0.0))
pc3 = f.cartesian_point((3.5, 0.0))
pc4 = f.cartesian_point((4.5, 0.0))
pc5 = f.cartesian_point((5.0, 0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('range_pc',2,"
    f"(#{pc0.eid},#{pc1.eid},#{pc2.eid},#{pc3.eid},#{pc4.eid},#{pc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,5.0,10.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('range_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('range_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('range_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('range_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
