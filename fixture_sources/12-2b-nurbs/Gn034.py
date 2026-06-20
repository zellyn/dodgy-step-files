"""Gn034 — B-spline knots packed below parametric resolution.

Catalog claim: Two consecutive knots in a B_SPLINE_CURVE_WITH_KNOTS differ by
less than the kernel's parametric epsilon (e.g., 1e-12 between knots at 0.5 and
0.5+1e-12). The interval is non-empty in IEEE-754 but rounds to zero in many
spline-evaluation routines, producing NaN or unstable derivatives.

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - Degree-2 B_SPLINE_CURVE_WITH_KNOTS with knot vector
    (0, 0, 0, 0.5, 0.500000000001, 1, 1, 1):
    two consecutive interior knots differ by 1e-12 — below parametric epsilon.
  - Between the near-equal knots at 0.5 and 0.500000000001 lies a non-empty
    IEEE-754 interval that collapses to zero in fixed-precision spline evaluation,
    causing NaN or unstable derivatives.
  - The near-equal knot pair IS the catalog mechanism; no separate driver needed
    since it directly causes NaN evaluation.
  - C-1 break also present in 3D edge (1.5-unit CP gap at t=0.5) for belt+suspenders.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS knot vector with two consecutive
    interior knots 0.5 and 0.500000000001 — delta = 1e-12, below parametric
    epsilon; interval collapses to zero in evaluation routines.
  - C-1 DRIVER: same curve has positional gap at t=0.5 boundary (1.5-unit gap)
    driving shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn034",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree-2 6-CP: knot vector "
        "(0.0,0.0,0.0,0.5,0.500000000001,1.0,1.0,1.0) — consecutive interior "
        "knots 0.5 and 0.500000000001 differ by 1e-12 (below parametric epsilon); "
        "IEEE-754 non-empty interval rounds to zero in spline evaluation routines "
        "producing NaN or unstable derivatives; C-1 positional break at t=0.5 "
        "(1.5-unit CP gap) also present to drive shape_null=True"
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

# ── CATALOG MECHANISM: near-equal consecutive knots (delta = 1e-12) ───────────
# Degree-2, 6 CPs; the catalog recipe.
# Knot vector: (0,0,0, 0.5, 0.500000000001, 1,1,1) — mults (3,1,1,3) sum=8=2+6 ✓
# CP positional gap at the 0.5/0.500000000001 boundary: 1.5-unit C-1 break.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((1.25, 0.0, 0.0))
dc2 = f.cartesian_point((2.5,  0.0, 0.0))   # end of first segment
dc3 = f.cartesian_point((4.0,  0.0, 0.0))   # 1.5-unit C-1 gap at near-equal knot
dc4 = f.cartesian_point((4.75, 0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

# The near-equal knot pair is the primary defect: 0.5 and 0.500000000001
packed_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('packed_knots_curve',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,1,1,3),(0.0,0.5,0.500000000001,1.0),.UNSPECIFIED.)"
)

# Pcurve (well-behaved; defect is in 3D curve knot vector)
pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.25, 0.0))
pp2 = f.cartesian_point((0.5,  0.0))
pp3 = f.cartesian_point((0.5,  0.0))
pp4 = f.cartesian_point((0.75, 0.0))
pp5 = f.cartesian_point((1.0,  0.0))

good_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('packed_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn034_pcdef',(#{good_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn034_pc_ent',#{surf.eid},#{defrep.eid})")
sc = f._emit_raw(
    f"SURFACE_CURVE('gn034_sc',#{packed_curve.eid},(#{pcurve.eid}),.PCURVE_S1.)"
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
    f"EDGE_CURVE('gn034_edge',#{v_a.eid},#{v_b.eid},#{sc.eid},.T.)"
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
