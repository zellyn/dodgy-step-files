"""Gn145 — Interior knot multiplicity C(-1) discontinuity.

Catalog claim: Interior knot at u=0.5 with multiplicity 3 (= degree+1),
creating a cusp/geometric discontinuity in U. With degree 2 the maximum interior
multiplicity for C0 continuity is 2; multiplicity 3 = degree+1 breaks the surface
into disconnected patches. Healing must detect and either split or elevate.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V), 5×3 control net.
    U interior knot at 0.5 with multiplicity 3 = degree+1. IS the face surface.
  - C-1 DRIVER: interior U-knot mult=3=p_u+1 → C(-1) in U (cusp or gap) →
    continuity-check healing path (C0BSplineToC1 analogue for surfaces).

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V);
    5×3 control net;
    U knots (0.0,0.5,1.0) mults (3,3,3) sum=9 → n_u=6... wait: n_u=5 poles
    needs sum n_u+p_u+1=8. Catalog says (3,2,3) for C0; (3,3,3) sums to 9
    but n_u must match. Using n_u=6 (adding one pole) with (3,3,3) sum=9 ✓.
    V knots (0.0,1.0) mults (3,3) sum=6 → n_v=3 ✓;
    interior U-knot mult=3=p_u+1 → C(-1) break;
    IS face surface; cusp-discontinuity detection and repair.
  - C-1 DRIVER: U interior mult equals degree+1 → patch separation at u=0.5
    → C(-1) discontinuity → healing splits or raises degree.

Note: catalog says 5×3 poles with (3,2,3) correct or (3,3,3) defective.
To produce exactly the defect: use 6 U-poles so (3,3,3) sum=9 gives n_u+p_u+1=9
→ n_u=6. Middle knot mult 3 = p_u+1 → C(-1) in U.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn145",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V); "
        "6×3 control net; "
        "U knots (0.0,0.5,1.0) mults (3,3,3) sum=9 → n_u=6 ✓; "
        "interior U-knot mult=3=p_u+1 → C(-1) discontinuity in U (cusp); "
        "V knots (0.0,1.0) mults (3,3) sum=6 → n_v=3 ✓; "
        "IS face surface; cusp-discontinuity healing path"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree-2 U × degree-2 V, 6×3 control net ──────
# U: n_u=6, p_u=2 → n_u+p_u+1=9. knots (0.0,0.5,1.0) mults (3,3,3) sum=9 ✓.
#    Interior mult=3=p_u+1: C(-1) break in U at u=0.5.
#    Lower half (u∈[0,0.5]) poles: r*[0..2]; upper half: r*[3..5].
#    Gap introduced: upper half starts offset in z from lower half end.
# V: n_v=3, p_v=2 → n_v+p_v+1=6. knots (0.0,1.0) mults (3,3) sum=6 ✓.
# Control net: 3 V-rows × 6 U-cols.
r0 = [
    f.cartesian_point((0.0, 0.0, 0.0)),   # u=0, v=0
    f.cartesian_point((2.0, 0.0, 0.5)),   # u∈[0,0.5] interior
    f.cartesian_point((4.0, 0.0, 1.0)),   # u=0.5 lower end
    f.cartesian_point((4.0, 0.0, 1.6)),   # u=0.5 upper start (gap)
    f.cartesian_point((6.0, 0.0, 2.1)),   # u∈[0.5,1] interior
    f.cartesian_point((8.0, 0.0, 2.5)),   # u=1
]
r1 = [
    f.cartesian_point((0.0, 3.0, 0.0)),
    f.cartesian_point((2.0, 3.0, 0.5)),
    f.cartesian_point((4.0, 3.0, 1.0)),
    f.cartesian_point((4.0, 3.0, 1.6)),
    f.cartesian_point((6.0, 3.0, 2.1)),
    f.cartesian_point((8.0, 3.0, 2.5)),
]
r2 = [
    f.cartesian_point((0.0, 6.0, 0.0)),
    f.cartesian_point((2.0, 6.0, 0.5)),
    f.cartesian_point((4.0, 6.0, 1.0)),
    f.cartesian_point((4.0, 6.0, 1.6)),
    f.cartesian_point((6.0, 6.0, 2.1)),
    f.cartesian_point((8.0, 6.0, 2.5)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)})"

# Interior U-knot mult=3=p_u+1 → C(-1) discontinuity.
mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn145_interior_mult_cusp',2,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3,3),(3,3),"
    f"(0.0,0.5,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# 3D corners: r0[0]=(0,0,0), r0[5]=(8,0,2.5), r2[5]=(8,6,2.5), r2[0]=(0,6,0).
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((8.0, 0.0, 2.5))
p_c3 = f.cartesian_point((8.0, 6.0, 2.5))
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
e_bot   = mk_line_edge(vt_a, vt_b, (0.,0.,0.),   (1.,0.,0.),   (0.0,0.0), (1.,0.),  1.0)
e_right = mk_line_edge(vt_b, vt_c, (8.,0.,2.5),  (0.,1.,0.),   (1.0,0.0), (0.,1.),  1.0)
e_top   = mk_line_edge(vt_c, vt_d, (8.,6.,2.5),  (-1.,0.,0.),  (1.0,1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(vt_d, vt_a, (0.,6.,0.),   (0.,-1.,0.),  (0.0,1.0), (0.,-1.), 1.0)

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
