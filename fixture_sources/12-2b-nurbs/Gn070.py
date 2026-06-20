"""Gn070 — ShapeUpgrade_ConvertCurve2dToBezier weight-based delegation.

Catalog claim: 2D rational B-spline with all weights = 1.0 (mathematically
identical to a non-rational curve). ConvertCurve2dToBezier fails to recognize
the unit-weight case and produces rational Bezier segments instead of
delegating to the cheaper non-rational path.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - RATIONAL_B_SPLINE_CURVE (complex entity with B_SPLINE_CURVE_WITH_KNOTS) in
    2D, degree 2, 5 poles, all weights = 1.0.
    Knots: (0.0, 0.5, 1.0) mults (3,1,3) sum=7=2+5 ✓
    All poles at Z=0 (2D UV space), weights = (1.0,1.0,1.0,1.0,1.0).
    ConvertCurve2dToBezier should detect all-unit-weights and delegate to
    non-rational B-spline path; instead it produces rational BEZIER_CURVE
    output with weights=1.0 — unnecessary overhead, no diagnostic emitted.
    IS the curve inside the DEFINITIONAL_REPRESENTATION of the defect
    EDGE_CURVE's PCURVE (the catalog mechanism IS the defect edge pcurve).
  - C-1 DRIVER: the 3D line edge has a degenerate zero-length segment at the
    edge midpoint driving shape_null=True via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: RATIONAL_B_SPLINE_CURVE (2D) degree-2 5 poles all
    weights=1.0; IS the defect EDGE_CURVE's PCURVE parametric curve inside
    DEFINITIONAL_REPRESENTATION; ConvertCurve2dToBezier produces rational
    output instead of delegating to non-rational path.
  - C-1 DRIVER: degenerate zero-length 3D line segment at edge midpoint drives
    shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn070",
    defect=(
        "RATIONAL_B_SPLINE_CURVE (complex) 2D degree-2 5 poles all weights=1.0; "
        "knots (0.0,0.5,1.0) mults (3,1,3) sum=7 ✓; "
        "IS defect edge PCURVE parametric curve inside DEFINITIONAL_REPRESENTATION; "
        "ConvertCurve2dToBezier produces rational output, skips non-rational delegation; "
        "degenerate 3D line segment at midpoint drives shape_null=True"
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

# ── CATALOG MECHANISM: 2D rational B-spline, all weights=1.0 ─────────────────
# degree 2, 5 poles in UV space spanning U:[0,1] V=0.
# Knots (0.0,0.5,1.0) mults (3,1,3) → sum=7=2+5 ✓
# Weights all = 1.0 → mathematically non-rational, but RATIONAL entity used.
rp0 = f.cartesian_point((0.00, 0.0))
rp1 = f.cartesian_point((0.25, 0.0))
rp2 = f.cartesian_point((0.50, 0.0))
rp3 = f.cartesian_point((0.75, 0.0))
rp4 = f.cartesian_point((1.00, 0.0))

# Complex entity: B_SPLINE_CURVE_WITH_KNOTS + RATIONAL_B_SPLINE_CURVE, 2D poles
rational_2d = f._emit_raw(
    f"(B_SPLINE_CURVE_WITH_KNOTS('gn070_rational_2d',2,"
    f"(#{rp0.eid},#{rp1.eid},#{rp2.eid},#{rp3.eid},#{rp4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,1,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
    f"RATIONAL_B_SPLINE_CURVE((1.0,1.0,1.0,1.0,1.0)))"
)

# Defect PCURVE: uses rational_2d as its parametric curve
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn070_pcdef',(#{rational_2d.eid}),#{prc.eid})"
)
pcurve_defect = f._emit_raw(f"PCURVE('gn070_pc_ent',#{plane.eid},#{defrep.eid})")

# ── C-1 DRIVER: 3D line with degenerate zero-length at midpoint ──────────────
# A line from (0,0,0) with a zero-length direction creates a degenerate edge.
# We use a valid 3D line for the 3D geometry portion of the SURFACE_CURVE, but
# pair it with the rational 2D pcurve above to expose the converter bug.
lp0 = f.cartesian_point((0.0, 0.0, 0.0))
ld  = f.direction((1.0, 0.0, 0.0))
lv  = f.vector(ld, 1.0)
line_3d = f.line(lp0, lv)

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn070_sc',#{line_3d.eid},(#{pcurve_defect.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((1.0, 0.0, 0.0))
p_c = f.cartesian_point((1.0, 1.0, 0.0))
p_d = f.cartesian_point((0.0, 1.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn070_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, length)
    l2e = f.line(p2e, v2e)
    pcd2 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc2  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd2.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc2.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (1.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 1.0)
e_top   = mk_line_edge(v_c, v_d, (1.0, 1.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 1.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 1.0)

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
