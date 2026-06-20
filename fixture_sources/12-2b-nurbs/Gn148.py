"""Gn148 — Ill-conditioned knot distribution.

Catalog claim: Interior knots clustered near 0 (0.001, 0.002) while the
boundary spans [0, 1]. The ratio > 1000:1 causes numerical instability in
fitting and evaluation. Healing must detect and reparametrize.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V), 4×3 control net.
    U knot vector (0.0, 0.001, 0.002, 1.0) mults (3,1,1,2)... wait: n_u=4,
    p_u=2 → sum=7. Catalog says U knots (0,0,0,0.001,0.002,1,1) which is
    a flat sequence; in mults form: (3,1,1,2) → sum=7 ✓. However catalog says
    "(3,2,2)" sums to 7 for 4 poles — let's use 2 interior knots (0.001, 0.002)
    each mult 1 to sum correctly: mults (3,1,1,2) = 7 ✓ with knots (0,0.001,0.002,1).
    IS the face surface.
  - C-1 DRIVER: interior knot spacing ratio (1.0-0.002)/(0.002-0.001) ≈ 998 >> 10
    → IsBad condition for knot spacing → arc-length reparametrization healing.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V);
    4×3 control net;
    U knots (0.0,0.001,0.002,1.0) mults (3,1,1,2) sum=7 → n_u=4 ✓;
    V knots (0.0,1.0) mults (3,3) sum=6 → n_v=3 ✓;
    IS face surface; extreme knot clustering near 0 → IsBad flag → reparametrize.
  - C-1 DRIVER: knot ratio (1.0-0.002)/(0.002-0.001) ≈ 998 exceeds threshold 10
    → Approx_CurvilinearParameter reparametrization triggered.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn148",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V); "
        "4×3 control net; "
        "U knots (0.0,0.001,0.002,1.0) mults (3,1,1,2) sum=7 → n_u=4 ✓; "
        "V knots (0.0,1.0) mults (3,3) sum=6 → n_v=3 ✓; "
        "IS face surface; knot clustering ratio ≈998:1 >> 10 → IsBad → reparametrize"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree-2 U × degree-2 V, 4×3 control net ──────
# U: n_u=4, p_u=2 → n_u+p_u+1=7.
#    knots (0.0,0.001,0.002,1.0) mults (3,1,1,2) sum=3+1+1+2=7 ✓.
#    Interior knots clustered at 0.001 and 0.002 → extreme ratio near boundary.
# V: n_v=3, p_v=2 → n_v+p_v+1=6. knots (0.0,1.0) mults (3,3) sum=6 ✓.
# Control net: 3 V-rows × 4 U-cols.
r0 = [
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.cartesian_point((1.0, 0.0, 0.5)),
    f.cartesian_point((3.0, 0.0, 0.5)),
    f.cartesian_point((9.0, 0.0, 0.0)),
]
r1 = [
    f.cartesian_point((0.0, 3.0, 0.0)),
    f.cartesian_point((1.0, 3.0, 0.5)),
    f.cartesian_point((3.0, 3.0, 0.5)),
    f.cartesian_point((9.0, 3.0, 0.0)),
]
r2 = [
    f.cartesian_point((0.0, 6.0, 0.0)),
    f.cartesian_point((1.0, 6.0, 0.5)),
    f.cartesian_point((3.0, 6.0, 0.5)),
    f.cartesian_point((9.0, 6.0, 0.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)})"

# Interior U-knots at 0.001 and 0.002 — extreme clustering near 0.
mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn148_ill_conditioned_knots',2,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,1,1,2),(3,3),"
    f"(0.0,0.001,0.002,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# 3D corners: r0[0]=(0,0,0), r0[3]=(9,0,0), r2[3]=(9,6,0), r2[0]=(0,6,0).
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((9.0, 0.0, 0.0))
p_c3 = f.cartesian_point((9.0, 6.0, 0.0))
p_d3 = f.cartesian_point((0.0, 6.0, 0.0))
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

# UV domain U∈[0,1] V∈[0,1].
e_bot   = mk_line_edge(vt_a, vt_b, (0.,0.,0.), (1.,0.,0.),   (0.0,0.0), (1.,0.),  1.0)
e_right = mk_line_edge(vt_b, vt_c, (9.,0.,0.), (0.,1.,0.),   (1.0,0.0), (0.,1.),  1.0)
e_top   = mk_line_edge(vt_c, vt_d, (9.,6.,0.), (-1.,0.,0.),  (1.0,1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(vt_d, vt_a, (0.,6.,0.), (0.,-1.,0.),  (0.0,1.0), (0.,-1.), 1.0)

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
