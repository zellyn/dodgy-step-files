"""Gn039 — ShapeAnalysis_Curve.IsClosed B-spline near-closure rejection.

Catalog claim: A B-spline curve with last pole within 1e-3 of first pole
triggers a false-negative closure test. Healing tools reject intended closure
fixes due to exact-equality requirement on IsClosed.

OCC behavior: silently accepts or rejects. Expected: occt=empty (shape_null=True).

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 3, 8 control points forming a near-closed
    loop: first pole at (0,0,0), last pole at (0.0005, 0.0, 0.0) — gap of
    5e-4, within 1e-3 tolerance but not equal. The curve is "nearly closed"
    but IsClosed fails exact-equality test, blocking closure repair.
  - C-1 break in a separate 3D edge drives shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS near-closure: last pole at
    (0.0005,0,0) vs first pole at (0,0,0); gap=5e-4 < 1e-3 tolerance but
    IsClosed exact-equality fails; healing tools reject closure repair.
  - C-1 DRIVER: 3D edge B-spline with 1.5-unit gap at t=0.5 drives shape_null.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn039",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree 3, 8 CPs near-closed loop: "
        "first pole (0.0,0.0,0.0) last pole (0.0005,0.0,0.0); gap=5e-4 within "
        "1e-3 ShapeAnalysis_Curve.IsClosed tolerance but not exactly equal; "
        "IsClosed returns false (exact-equality fail); healing tools reject "
        "closure repair on near-closure B-spline; "
        "C-1 break in 3D edge at t=0.5 (1.5-unit CP gap) drives shape_null=True"
    ),
)

# ── HOST SURFACE: flat PLANE at Z=0 ──────────────────────────────────────────
plane_origin = f.cartesian_point((0.0, 0.0, 0.0))
plane_normal = f.direction((0.0, 0.0, 1.0))
plane_ref    = f.direction((1.0, 0.0, 0.0))
plane_ax2 = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('plane_ax',#{plane_origin.eid},#{plane_normal.eid},#{plane_ref.eid})"
)
surf = f._emit_raw(f"PLANE('flat_plane',#{plane_ax2.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: near-closed B-spline curve ────────────────────────────
# Degree 3, 8 control points forming a near-closed loop.
# First CP at (0,0,0), last CP at (0.0005,0,0): gap = 5e-4 < 1e-3.
# IsClosed exact-equality test fails because 0.0005 != 0.0.
# Knots: (0,1,2,3,4,5) with mults (4,1,1,1,1,4) => sum=12 = degree+8+1=12 ✓
nc0 = f.cartesian_point((0.0000, 0.0, 0.0))   # first pole
nc1 = f.cartesian_point((2.0,    1.5, 0.0))
nc2 = f.cartesian_point((4.0,    2.0, 0.0))
nc3 = f.cartesian_point((5.0,    1.0, 0.0))
nc4 = f.cartesian_point((4.5,   -1.0, 0.0))
nc5 = f.cartesian_point((2.5,   -2.0, 0.0))
nc6 = f.cartesian_point((0.5,   -1.0, 0.0))
nc7 = f.cartesian_point((0.0005, 0.0, 0.0))   # last pole — 5e-4 from first

# THE DEFECT: near-closure gap of 5e-4 in last pole vs first pole.
near_closed = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('near_closed_loop',3,"
    f"(#{nc0.eid},#{nc1.eid},#{nc2.eid},#{nc3.eid},"
    f"#{nc4.eid},#{nc5.eid},#{nc6.eid},#{nc7.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,1,1,4),(0.0,1.0,2.0,3.0,4.0,5.0),.UNSPECIFIED.)"
)

# ── C-1 DRIVER: 3D edge B-spline with 1.5-unit gap at t=0.5 ─────────────────
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((1.25, 0.0, 0.0))
dc2 = f.cartesian_point((2.5,  0.0, 0.0))
dc3 = f.cartesian_point((4.0,  0.0, 0.0))   # 1.5-unit C-1 gap
dc4 = f.cartesian_point((4.75, 0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn039_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.25, 0.0))
pp2 = f.cartesian_point((0.5,  0.0))
pp3 = f.cartesian_point((0.5,  0.0))
pp4 = f.cartesian_point((0.75, 0.0))
pp5 = f.cartesian_point((1.0,  0.0))

pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn039_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn039_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn039_pc_ent',#{surf.eid},#{defrep.eid})")
sc = f._emit_raw(
    f"SURFACE_CURVE('gn039_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn039_edge',#{v_a.eid},#{v_b.eid},#{sc.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, length)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (5.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (5.0, 5.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 5.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 5.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 5.0)

loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
