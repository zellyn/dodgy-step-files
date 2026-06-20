"""Gn154 — Rational B-spline with zero-weight pole singularity.

Catalog claim: Minimal reproducer: RATIONAL_B_SPLINE_SURFACE, 3×3 control net,
degree (2,2). Interior pole P[1,1] has weight w=0. Knot structure: U,V
multiplicities (3,3)/(3,3), fully clamped. Healing challenge: weight=0 creates
homogeneous singularity (w=0 in rational plane); rational evaluation undefined
at that pole. Expected: flag pole degenerate or skip in geometric computation.

STEP mechanism (literal):
  - Complex RATIONAL_B_SPLINE_SURFACE: B_SPLINE_SURFACE degree=2 (U) × 2 (V),
    3×3 control net. Interior pole P[1,1] weight=0.0. U/V knots (0.0,1.0)
    mults (3,3) sum=6 → n_u=3, n_v=3 ✓. Rational flag .T. IS the face surface;
    zero-weight interior pole creates homogeneous singularity.
  - C-1 DRIVER: weight=0 at P[1,1] → denominator=0 in rational evaluation →
    IsBad flag; healer must flag degenerate pole or clamp to eps.

Mechanism vs driver:
  - CATALOG MECHANISM: RATIONAL_B_SPLINE_SURFACE degree=2 (U) × 2 (V);
    3×3 control net; U/V knots (0.0,1.0) mults (3,3) sum=6 → n=3 ✓;
    weights ((1,1,1),(1,0,1),(1,1,1)) → P[1,1] weight=0; IS face surface;
    homogeneous singularity → degenerate-pole detection.
  - C-1 DRIVER: rational denominator=0 → flag degenerate or clamp to eps.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn154",
    defect=(
        "RATIONAL_B_SPLINE_SURFACE degree=2 (U) × 2 (V); "
        "3×3 control net; U/V knots (0.0,1.0) mults (3,3) sum=6 → n=3 ✓; "
        "weights ((1,1,1),(1,0,1),(1,1,1)) → P[1,1] weight=0; IS face surface; "
        "homogeneous singularity (w=0) → degenerate-pole detection or eps-clamp"
    ),
)

# ── Control net: 3 V-rows × 3 U-cols ─────────────────────────────────────────
# Bilinear-ish shape; interior pole at (2,2,0.5) with weight=0 → singularity.
r0 = [
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.cartesian_point((2.0, 0.0, 0.3)),
    f.cartesian_point((4.0, 0.0, 0.0)),
]
r1 = [
    f.cartesian_point((0.0, 2.0, 0.3)),
    f.cartesian_point((2.0, 2.0, 0.5)),   # weight=0 → homogeneous singularity
    f.cartesian_point((4.0, 2.0, 0.3)),
]
r2 = [
    f.cartesian_point((0.0, 4.0, 0.0)),
    f.cartesian_point((2.0, 4.0, 0.3)),
    f.cartesian_point((4.0, 4.0, 0.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)})"

# Rational complex entity: weight=0 at P[1,1] → homogeneous singularity.
mech_surf = f._emit_raw(
    f"(B_SPLINE_SURFACE(2,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.)"
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn154_zero_weight_singularity',"
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

# ── Boundary edges on the rational surface ─────────────────────────────────────
# 3D corners at surface parametric boundary (u=0 or 1, v=0 or 1):
# r0[0]=(0,0,0), r0[2]=(4,0,0), r2[2]=(4,4,0), r2[0]=(0,4,0).
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((4.0, 0.0, 0.0))
p_c3 = f.cartesian_point((4.0, 4.0, 0.0))
p_d3 = f.cartesian_point((0.0, 4.0, 0.0))
vt_a = f.vertex_point(p_a3)
vt_b = f.vertex_point(p_b3)
vt_c = f.vertex_point(p_c3)
vt_d = f.vertex_point(p_d3)

def mk_line_edge(vs_, ve_, p3c, d3t, p2t, d2t, length):
    p3e  = f.cartesian_point(p3c)
    d3e  = f.direction(d3t)
    v3_  = f.vector(d3e, length)
    l3   = f.line(p3e, v3_)
    p2e  = f.cartesian_point(p2t)
    d2e  = f.direction(d2t)
    v2_  = f.vector(d2e, length)
    l2_  = f.line(p2e, v2_)
    pcd_ = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2_.eid}),#{prc.eid})")
    pc_  = f._emit_raw(f"PCURVE('pc',#{mech_surf.eid},#{pcd_.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc_.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs_.eid},#{ve_.eid},#{sc_.eid},.T.)")

# UV domain U∈[0,1] V∈[0,1]; 3D boundary at z=0 (flat corners).
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
