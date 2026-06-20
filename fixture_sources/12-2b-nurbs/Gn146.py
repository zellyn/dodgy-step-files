"""Gn146 — Rational NURBS singular weight.

Catalog claim: Rational B-spline surface (weights present) with singular
weight 0.0 at the middle pole. The weighted control point is geometrically
removed; healing must detect and handle the weight singularity.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V), 3×3 control net.
    Weights row-major: (1,1,1), (1,0,1), (1,1,1). Center pole p[1][1] has
    weight 0.0. IS the face surface (rational flag .T.).
  - C-1 DRIVER: rational weight=0 at interior pole → denominator singularity
    in rational basis evaluation → healing must clamp or replace zero weight.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V);
    3×3 control net; U knots (0.0,1.0) mults (3,3) sum=6 → n_u=3 ✓;
    V knots (0.0,1.0) mults (3,3) sum=6 → n_v=3 ✓;
    rational .T.; weights ((1,1,1),(1,0,1),(1,1,1)) → center weight=0;
    IS face surface; weight singularity → division-by-zero healing path.
  - C-1 DRIVER: weight=0 at p[1][1] → rational denominator = 0 → undefined
    evaluation → weight-clamp healing (clamp to [eps,1]).

Note: STEP encodes rational B-spline surfaces via the RATIONAL_B_SPLINE_SURFACE
entity mixed with B_SPLINE_SURFACE_WITH_KNOTS in a complex entity. We encode
the rational flag as .T. in the B_SPLINE_SURFACE entity and embed the weights
via the RATIONAL_B_SPLINE_SURFACE subtype in a complex instance.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn146",
    defect=(
        "Rational B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V); "
        "3×3 control net; U/V knots (0.0,1.0) mults (3,3) sum=6 → n=3 ✓; "
        "rational .T.; weights ((1,1,1),(1,0,1),(1,1,1)); center weight=0; "
        "IS face surface; weight=0 → denominator singularity → weight-clamp healing"
    ),
)

# ── Control net: 3 V-rows × 3 U-cols ─────────────────────────────────────────
# Surface spans x∈[0,4], y∈[0,4], z slightly elevated at edges.
# U: n_u=3, p_u=2 → sum=6. V: n_v=3, p_v=2 → sum=6.
r0 = [
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.cartesian_point((2.0, 0.0, 0.5)),
    f.cartesian_point((4.0, 0.0, 0.0)),
]
r1 = [
    f.cartesian_point((0.0, 2.0, 0.5)),
    f.cartesian_point((2.0, 2.0, 1.0)),   # center pole; weight=0 → singularity
    f.cartesian_point((4.0, 2.0, 0.5)),
]
r2 = [
    f.cartesian_point((0.0, 4.0, 0.0)),
    f.cartesian_point((2.0, 4.0, 0.5)),
    f.cartesian_point((4.0, 4.0, 0.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)})"

# STEP rational B-spline surface: complex entity combining
# B_SPLINE_SURFACE + B_SPLINE_SURFACE_WITH_KNOTS + RATIONAL_B_SPLINE_SURFACE.
# Weights listed row-major matching control net order.
mech_surf = f._emit_raw(
    f"(B_SPLINE_SURFACE(2,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.)"
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn146_rational_zero_weight',"
    f"(3,3),(3,3),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
    f"RATIONAL_B_SPLINE_SURFACE("
    f"((1.0,1.0,1.0),(1.0,0.0,1.0),(1.0,1.0,1.0)))"
    f"REPRESENTATION_ITEM('')"
    f"SURFACE())"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# 3D corners: r0[0]=(0,0,0), r0[2]=(4,0,0), r2[2]=(4,4,0), r2[0]=(0,4,0).
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((4.0, 0.0, 0.0))
p_c3 = f.cartesian_point((4.0, 4.0, 0.0))
p_d3 = f.cartesian_point((0.0, 4.0, 0.0))
vt_a = f.vertex_point(p_a3)
vt_b = f.vertex_point(p_b3)
vt_c = f.vertex_point(p_c3)
vt_d = f.vertex_point(p_d3)

def mk_line_edge(vs_, ve_, p3c, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3c)
    d3e = f.direction(d3t)
    v3_ = f.vector(d3e, length)
    l3  = f.line(p3e, v3_)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2_ = f.vector(d2e, length)
    l2_ = f.line(p2e, v2_)
    pcd_ = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2_.eid}),#{prc.eid})")
    pc_  = f._emit_raw(f"PCURVE('pc',#{mech_surf.eid},#{pcd_.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc_.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs_.eid},#{ve_.eid},#{sc_.eid},.T.)")

# UV domain U∈[0,1] V∈[0,1]; 3D boundary is a flat quad.
e_bot   = mk_line_edge(vt_a, vt_b, (0.,0.,0.), (1.,0.,0.),   (0.0,0.0), (1.,0.),  1.0)
e_right = mk_line_edge(vt_b, vt_c, (4.,0.,0.), (0.,1.,0.),   (1.0,0.0), (0.,1.),  1.0)
e_top   = mk_line_edge(vt_c, vt_d, (4.,4.,0.), (-1.,0.,0.),  (1.0,1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(vt_d, vt_a, (0.,4.,0.), (0.,-1.,0.),  (0.0,1.0), (0.,-1.), 1.0)

loop  = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], mech_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
