"""Gn060 — ShapeUpgrade_ConvertCurve2dToBezier loop-variable persistence.

Catalog claim: 2D B-spline with 6+ segments (degree 2, 9 control points).
Loop variable j1 doesn't reset between outer iterations, causing patch skip
during C0→Bezier decomposition. Knot multiplicities create multiple continuity
breaks.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree-2, 8 control points (2D in UV).
    Knots: (0.0, 0.25, 0.5, 0.67, 0.83, 1.0) mults (3,2,1,1,1,3) sum=11=2+8+1 ✓
    5 spans with C0/C1 junctions; wavy UV trajectory oscillates in V direction.
    IS the pcurve (DEFINITIONAL_REPRESENTATION B-spline) of the defect
    EDGE_CURVE's SURFACE_CURVE.
    ShapeUpgrade_ConvertCurve2dToBezier iterates over spans; j1 not reset
    between outer loop iterations → patch-skip causes incorrect decomposition.
  - C-1 DRIVER: same entity — the oscillating pcurve combined with the patch-
    skip produces a degenerate 2D parameterization that drives shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree-2 8 CPs 2D UV;
    IS defect edge pcurve; ConvertCurve2dToBezier j1 loop-variable persistence
    causes patch skip across 5-span UV B-spline.
  - C-1 DRIVER: same entity — degenerate pcurve geometry drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn060",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree-2 8 poles 2D UV; "
        "knots (0.0,0.25,0.5,0.67,0.83,1.0) mults (3,2,1,1,1,3) sum=11 ✓; "
        "5 spans wavy UV trajectory; IS defect edge pcurve B-spline; "
        "ShapeUpgrade_ConvertCurve2dToBezier j1 not reset between outer "
        "iterations — patch skip produces degenerate 2D parameterization; "
        "drives shape_null=True"
    ),
)

# ── Flat plane for the face ──────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('ax3',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('face_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── 3D line for defect EDGE_CURVE (mechanism lives in the pcurve) ─────────────
p3_a = f.cartesian_point((0.0, 0.0, 0.0))
p3_b = f.cartesian_point((1.0, 0.0, 0.0))
d3   = f.direction((1.0, 0.0, 0.0))
v3   = f.vector(d3, 1.0)
l3   = f.line(p3_a, v3)

# ── CATALOG MECHANISM: 2D B-spline pcurve with 8 CPs, 5 spans ────────────────
# degree-2, 8 CPs in UV space. 5 interior simple knots (C1 junctions).
# n=8 CPs, p=2: knot count=8+2+1=11.
# Knots (0.0,0.2,0.4,0.6,0.8,1.0) mults (3,1,1,1,1,3): sum=3+1+1+1+1+3=10 ✗
# Correction: need sum=11. Use (3,1,1,1,2,3): sum=11 ✓
# Or simpler: 8 CPs gives n+p+1=11. Use (3,2,1,1,1,3) sum=11 ✓ — 4 interior distinct.
# Final: knots (0.0,0.25,0.5,0.67,0.83,1.0) mults (3,2,1,1,1,3) sum=11 ✓
q0 = f.cartesian_point((0.00, 0.00))
q1 = f.cartesian_point((0.14, 0.15))
q2 = f.cartesian_point((0.28, 0.00))
q3 = f.cartesian_point((0.43, 0.15))
q4 = f.cartesian_point((0.57, 0.00))
q5 = f.cartesian_point((0.71, 0.15))
q6 = f.cartesian_point((0.86, 0.00))
q7 = f.cartesian_point((1.00, 0.00))

# n=8 CPs, p=2: sum of mults must = 11.
# knots (0.0,0.25,0.5,0.67,0.83,1.0) mults (3,2,1,1,1,3) = 11 ✓ → 5 spans (C0 at t=0.25)
pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn060_pc_bspline',2,"
    f"(#{q0.eid},#{q1.eid},#{q2.eid},#{q3.eid},#{q4.eid},#{q5.eid},#{q6.eid},#{q7.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,2,1,1,1,3),(0.0,0.25,0.5,0.67,0.83,1.0),.UNSPECIFIED.)"
)

pcd = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn060_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn060_pc_ent',#{plane.eid},#{pcd.eid})")

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn060_sc',#{l3.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((1.0, 0.0, 0.0))
p_c = f.cartesian_point((1.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn060_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, length)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, length)
    l2e = f.line(p2e, v2e)
    pcd2 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc2  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd2.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc2.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (1.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (1.0, 5.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 5.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 5.0)

loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
