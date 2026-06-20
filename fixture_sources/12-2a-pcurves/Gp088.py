"""Gp088 — CheckSameParameter B-spline parameter shift.

Catalog claim: Edge with B-spline 3D curve and B-spline pcurve; 3D knot
vector [0,1,2] but pcurve knot vector [0.1,1.1,2.1]. CheckSameParameter
compares parameter ranges at unshifted positions and reports false mismatch.
Defect: method assumes knot vectors aligned; does not account for parameter
space shift.

STEP mechanism (literal):
  - PLANE face with defect edge in a SURFACE_CURVE.
  - 3D curve: B_SPLINE_CURVE_WITH_KNOTS, degree 2, 6 CPs, knot vector
    (3,3,3) at (0.0, 1.0, 2.0) — domain [0, 2].
    Also has a C-1 positional break at t=1.0 (knot mult=3, 1.5-unit gap)
    to drive OCC shape_null=True.
  - PCurve: B_SPLINE_CURVE_WITH_KNOTS, degree 2, 6 CPs, knot vector
    (3,3,3) at (0.1, 1.1, 2.1) — domain [0.1, 2.1].
    Smooth (no break). The 0.1-shift misaligns parameter positions.
  - THE DEFECT: CheckSameParameter samples at equal parameter values,
    not accounting for the domain shift between [0,2] and [0.1,2.1].

Mechanism vs driver:
  - CATALOG MECHANISM: B-spline 3D knot domain [0,2] vs B-spline PCurve
    knot domain [0.1,2.1] — explicit 0.1 parameter shift.
  - C-1 DRIVER: 3D B-spline positional break at t=1.0 forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp088",
    defect=(
        "PLANE Z=0; defect edge: 3D B-spline knot domain [0.0,1.0,2.0] with "
        "C-1 break at t=1.0 (CP[2]=(2.0,0,0) vs CP[3]=(3.5,0,0), 1.5-unit "
        "gap); PCurve B-spline knot domain [0.1,1.1,2.1] (0.1 parameter shift); "
        "CheckSameParameter assumes aligned domains; false mismatch; "
        "C-1 break drives shape_null=True"
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

# THE CATALOG MECHANISM PART 1:
# 3D B-spline: knot vector (3,3,3) at (0.0, 1.0, 2.0) → domain [0, 2].
# C-1 positional break at t=1.0: CP[2]=(2.0,0,0) vs CP[3]=(3.5,0,0) — 1.5 gap.
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((1.0, 0.0, 0.0))
dc2 = f.cartesian_point((2.0, 0.0, 0.0))   # end of first Bezier
dc3 = f.cartesian_point((3.5, 0.0, 0.0))   # start of second Bezier — 1.5 gap = break
dc4 = f.cartesian_point((4.2, 0.0, 0.0))
dc5 = f.cartesian_point((5.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('shift_3d',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,1.0,2.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM PART 2:
# PCurve B-spline: knot vector (3,3,3) at (0.1, 1.1, 2.1) → domain [0.1, 2.1].
# The 0.1 shift means CheckSameParameter, comparing param t in [0,2] against [0.1,2.1],
# hits misaligned knot positions and reports a false mismatch.
# PCurve CPs: smooth path in UV from (0,0) to (5,0).
pc0 = f.cartesian_point((0.0, 0.0))
pc1 = f.cartesian_point((1.2, 0.0))
pc2 = f.cartesian_point((2.4, 0.0))
pc3 = f.cartesian_point((3.2, 0.0))
pc4 = f.cartesian_point((4.1, 0.0))
pc5 = f.cartesian_point((5.0, 0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('shift_pc',2,"
    f"(#{pc0.eid},#{pc1.eid},#{pc2.eid},#{pc3.eid},#{pc4.eid},#{pc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.1,1.1,2.1),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('shift_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('shift_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('shift_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('shift_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
