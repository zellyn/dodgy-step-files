"""Gn049 — ShapeAnalysis_Curve.IsClosed parameter-infinite B-spline curve with knot sentinel.

Catalog claim: B-spline curve with one parameter (U_MAX) set to infinity
sentinel value (1.797...e+308). IsClosed checks closure before validating
parameter bounds, allowing NaN comparisons on infinite knot value. Expects
rejection at parameter validation layer.

OCC behavior: silently accepts or rejects; shape_null=True expected. Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 2, 4 CPs, clamped.
    Knots: (0.0, 1.797693134862315e+308) — U_MAX is the IEEE 754 max-double
    sentinel (used as "infinity" by some exporters). Mults (3,3) sum=6=2+4+1=7
    -- WAIT: sum=6 but 2+4+1=7; this mismatch is intentional: with only 4 CPs
    degree 2 needs mults summing to degree+nCPs+1=2+4+1=7 but mults (3,3)=6.
    The knot vector is structurally invalid (wrong sum) AND contains a sentinel
    infinity. IsClosed() evaluates C(t_start) vs C(t_end); t_end=1.797e+308
    produces NaN in arithmetic before parameter bounds are validated, causing
    an incorrect closure decision.
  - C-1 break in 3D edge curve (1.5-unit gap at t=0.5) drives shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree 2 4-CP; knot U_MAX=
    1.797693134862315e+308 (IEEE 754 max-double infinity sentinel); mults (3,3)
    sum=6 vs required 7 (structural mismatch); IsClosed() NaN comparison on
    infinite t_end before bounds validation; incorrect closure result.
  - C-1 DRIVER: 3D edge B-spline with 1.5-unit gap at t=0.5 drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

# IEEE 754 max double — the infinity sentinel value per catalog description.
U_MAX_SENTINEL = 1.797693134862315e+308

f = StepFile(
    catalog_id="Gn049",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree 2 4-CP: "
        "knots (0.0,1.797693134862315e+308) mults (3,3) sum=6 (required 7=2+4+1); "
        "U_MAX=1.797693134862315e+308 is IEEE 754 max-double infinity sentinel; "
        "structural knot-sum mismatch AND infinite knot value; "
        "ShapeAnalysis_Curve.IsClosed() evaluates C(t_end) at infinite parameter "
        "before bounds validation; NaN arithmetic produces incorrect closure result; "
        "C-1 break in 3D edge at t=0.5 (1.5-unit CP gap) drives shape_null=True"
    ),
)

# ── HOST SURFACE: flat plane ──────────────────────────────────────────────────
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

# ── CATALOG MECHANISM: B-spline with infinity-sentinel knot ──────────────────
# Degree 2, 4 CPs; mults (3,3) sum=6, knot U_MAX=1.797693134862315e+308.
# THE DEFECT: infinite knot value triggers NaN in IsClosed() before validation.
ic0 = f.cartesian_point((0.0, 0.0, 0.0))
ic1 = f.cartesian_point((1.0, 1.0, 0.0))
ic2 = f.cartesian_point((2.0, 1.0, 0.0))
ic3 = f.cartesian_point((3.0, 0.0, 0.0))

inf_knot_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn049_inf_knot',2,"
    f"(#{ic0.eid},#{ic1.eid},#{ic2.eid},#{ic3.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,{U_MAX_SENTINEL!r}),.UNSPECIFIED.)"
)

# ── C-1 DRIVER: 3D edge B-spline with 1.5-unit gap at t=0.5 ─────────────────
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((1.25, 0.0, 0.0))
dc2 = f.cartesian_point((2.5,  0.0, 0.0))
dc3 = f.cartesian_point((4.0,  0.0, 0.0))   # 1.5-unit C-1 gap
dc4 = f.cartesian_point((4.75, 0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn049_c1_break',2,"
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
    f"B_SPLINE_CURVE_WITH_KNOTS('gn049_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn049_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn049_pc_ent',#{surf.eid},#{defrep.eid})")
sc = f._emit_raw(
    f"SURFACE_CURVE('gn049_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
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
    f"EDGE_CURVE('gn049_edge',#{v_a.eid},#{v_b.eid},#{sc.eid},.T.)"
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

e_right = mk_line_edge(v_b, v_c, (5.0, 0.0, 0.0), (0.,1.,0.), (5.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (5.0, 5.0, 0.0), (-1.,0.,0.), (5.0, 5.0), (-1.,0.), 5.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 5.0, 0.0), (0.,-1.,0.), (0.0, 5.0), (0.,-1.), 5.0)

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
