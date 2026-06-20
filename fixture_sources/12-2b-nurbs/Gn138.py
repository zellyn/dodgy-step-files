"""Gn138 — NURBS trimmed surface Bezier basis delegation.

Catalog claim: Surface with 5x4 grid, degree 2/2. Compute delegates to basis
surface recursively for trimmed surfaces. Parameter domain mismatch between
trimmed range and basis surface conversion causes bounds validation failure.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V), 5×4 control net.
    Three U-interior knots and two V-interior knots produce a multi-patch Bezier
    decomposition. IS the face surface (mechanism IS the face surface).
  - C-1 DRIVER: recursive Bezier basis conversion over multi-patch surface →
    parameter domain sync between trimmed range and basis conversion fails →
    bounds validation error.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V);
    5×4 control net; U knots (0.0, 0.5, 1.0) mults (3,2,3) sum=8 → n_u=5 ✓;
    V knots (0.0, 0.5, 1.0) mults (3,1,3) sum=7 → n_v=4 ✓; IS face surface;
    ConvertSurfaceToBezierBasis recursive delegation → bounds mismatch.
  - C-1 DRIVER: parameter domain mismatch between trimmed range and basis
    surface conversion in recursive Bezier delegation.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn138",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V); "
        "5×4 control net; "
        "U knots (0.0,0.5,1.0) mults (3,2,3) sum=8 → n_u=5; "
        "V knots (0.0,0.5,1.0) mults (3,1,3) sum=7 → n_v=4; "
        "IS face surface; ConvertSurfaceToBezierBasis recursive delegation → "
        "parameter domain mismatch → bounds validation failure"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree-2 U × degree-2 V, 5×4 control net ──────
# U: n_u=5, p_u=2 → n_u+p_u+1=8. knots (0.0,0.5,1.0) mults (3,2,3) sum=8 ✓.
#    Interior knot at 0.5 (mult 2) creates two Bezier patches in U.
# V: n_v=4, p_v=2 → n_v+p_v+1=7. knots (0.0,0.5,1.0) mults (3,1,3) sum=7 ✓.
#    Interior knot at 0.5 (mult 1 < degree) creates C1 joint; two patches in V.
# Control net: 4 V-rows × 5 U-cols, spread over x=0..8, y=0..6.
r0 = [
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.cartesian_point((2.0, 0.5, 0.0)),
    f.cartesian_point((4.0, 0.3, 0.0)),
    f.cartesian_point((6.0, 0.6, 0.0)),
    f.cartesian_point((8.0, 0.0, 0.0)),
]
r1 = [
    f.cartesian_point((0.0, 2.0, 0.5)),
    f.cartesian_point((2.0, 2.5, 0.8)),
    f.cartesian_point((4.0, 2.3, 1.0)),
    f.cartesian_point((6.0, 2.6, 0.8)),
    f.cartesian_point((8.0, 2.0, 0.5)),
]
r2 = [
    f.cartesian_point((0.0, 4.0, 0.5)),
    f.cartesian_point((2.0, 4.5, 0.6)),
    f.cartesian_point((4.0, 4.3, 0.8)),
    f.cartesian_point((6.0, 4.6, 0.6)),
    f.cartesian_point((8.0, 4.0, 0.5)),
]
r3 = [
    f.cartesian_point((0.0, 6.0, 0.0)),
    f.cartesian_point((2.0, 6.5, 0.0)),
    f.cartesian_point((4.0, 6.3, 0.0)),
    f.cartesian_point((6.0, 6.6, 0.0)),
    f.cartesian_point((8.0, 6.0, 0.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)},{row_ids(r3)})"

mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn138_bezier_delegate',2,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,2,3),(3,1,3),"
    f"(0.0,0.5,1.0),(0.0,0.5,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# 3D corners: r0[0]=(0,0,0), r0[4]=(8,0,0), r3[4]=(8,6,0), r3[0]=(0,6,0).
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((8.0, 0.0, 0.0))
p_c3 = f.cartesian_point((8.0, 6.0, 0.0))
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

# UV domain U∈[0,1] V∈[0,1]; 3D corners above.
e_bot   = mk_line_edge(vt_a, vt_b, (0.,0.,0.),  (1.,0.,0.),  (0.0,0.0), (1.,0.), 1.0)
e_right = mk_line_edge(vt_b, vt_c, (8.,0.,0.),  (0.,1.,0.),  (1.0,0.0), (0.,1.), 1.0)
e_top   = mk_line_edge(vt_c, vt_d, (8.,6.,0.),  (-1.,0.,0.), (1.0,1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(vt_d, vt_a, (0.,6.,0.),  (0.,-1.,0.), (0.0,1.0), (0.,-1.), 1.0)

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
