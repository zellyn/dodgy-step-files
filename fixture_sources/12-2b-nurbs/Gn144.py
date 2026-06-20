"""Gn144 — Periodic knot-vector closure mismatch.

Catalog claim: Periodic B-spline surface (.T. in U) with open-clamped knot
vector. The surface is marked U_CLOSED=.T. (periodic flag) but the knot vector
uses clamped multiplicities (3,3) that conflict with 4-pole periodic topology.
Healing must validate periodic-flag consistency against the knot structure.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V), 4×3 control net,
    U_CLOSED=.T. IS the face surface.
  - C-1 DRIVER: 4 poles U + degree 2 → 7 knot values needed. Clamped (3,3)
    only sums to 6 — one short. Periodic-flag consistency check detects the
    knot-count conflict and triggers closure-repair logic.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V);
    4×3 control net; U_CLOSED=.T.;
    U knots (0.0,1.0) mults (3,3) sum=6 → 4 poles needs sum=7 → mismatch;
    V knots (0.0,1.0) mults (3,3) sum=6 → n_v=3 ✓;
    IS face surface; periodic-flag vs knot-structure inconsistency.
  - C-1 DRIVER: periodic flag .T. with clamped knot sum one short → closure
    check detects mismatch → knot-repair / re-parametrization healing path.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn144",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V); "
        "4×3 control net; U_CLOSED=.T. (periodic flag); "
        "U knots (0.0,1.0) mults (3,3) sum=6 → 4 poles+degree 2 needs 7 → mismatch; "
        "V knots (0.0,1.0) mults (3,3) sum=6 → n_v=3 ✓; "
        "IS face surface; periodic-flag vs clamped-knot-count conflict"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree-2 U × degree-2 V, 4×3 control net ──────
# U: n_u=4, p_u=2 → needs n_u+p_u+1=7. Clamped (3,3) gives only 6 → MISMATCH.
#    U_CLOSED=.T. declares periodic intent but knot vector is clamped.
# V: n_v=3, p_v=2 → n_v+p_v+1=6. knots (0.0,1.0) mults (3,3) sum=6 ✓.
# Control net: 3 V-rows × 4 U-cols; U-poles form a rough closed loop.
r0 = [
    f.cartesian_point(( 1.0,  0.0, 0.0)),
    f.cartesian_point(( 0.0,  1.0, 0.0)),
    f.cartesian_point((-1.0,  0.0, 0.0)),
    f.cartesian_point(( 0.0, -1.0, 0.0)),
]
r1 = [
    f.cartesian_point(( 1.0,  0.0, 0.5)),
    f.cartesian_point(( 0.0,  1.0, 0.5)),
    f.cartesian_point((-1.0,  0.0, 0.5)),
    f.cartesian_point(( 0.0, -1.0, 0.5)),
]
r2 = [
    f.cartesian_point(( 1.0,  0.0, 1.0)),
    f.cartesian_point(( 0.0,  1.0, 1.0)),
    f.cartesian_point((-1.0,  0.0, 1.0)),
    f.cartesian_point(( 0.0, -1.0, 1.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)})"

# U_CLOSED=.T. with clamped (3,3) knots → 6 sum vs 7 needed → mismatch defect.
mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn144_periodic_closure_mismatch',2,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.T.,.F.,.F.,"
    f"(3,3),(3,3),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# 3D corners: r0[0]=(1,0,0), r0[3]=(0,-1,0), r2[3]=(0,-1,1), r2[0]=(1,0,1).
p_a3 = f.cartesian_point(( 1.0,  0.0, 0.0))
p_b3 = f.cartesian_point(( 0.0, -1.0, 0.0))
p_c3 = f.cartesian_point(( 0.0, -1.0, 1.0))
p_d3 = f.cartesian_point(( 1.0,  0.0, 1.0))
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

# UV domain U∈[0,1] V∈[0,1]; seam at U=0.
e_bot   = mk_line_edge(vt_a, vt_b, ( 1., 0.,0.),  (0.,0.,0.),  (0.0,0.0), (1.,0.), 1.0)
e_right = mk_line_edge(vt_b, vt_c, ( 0.,-1.,0.),  (0.,0.,1.),  (1.0,0.0), (0.,1.), 1.0)
e_top   = mk_line_edge(vt_c, vt_d, ( 0.,-1.,1.),  (0.,0.,0.),  (1.0,1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(vt_d, vt_a, ( 1., 0.,1.),  (0.,0.,-1.), (0.0,1.0), (0.,-1.), 1.0)

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
