"""Gn140 — U-Periodic Surface with V-Bounds Check Mismatch.

Catalog claim: U-periodic B-spline surface where V-parameter bounds in the trim
region differ from the surface's natural V-domain. Healers that check V-bounds
after converting the periodic U-direction may apply the wrong domain limits,
causing a V-bounds mismatch failure.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V), 5×4 control net,
    U_CLOSED=.T. IS the face surface.
  - C-1 DRIVER: U_CLOSED=.T. with non-trivial V-knot range (0.0..2.0 not 0.0..1.0)
    → V-bounds check after periodic U conversion applies incorrect [0,1] limit
    → V-bounds mismatch failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V);
    5×4 control net; U_CLOSED=.T.;
    U knots (0.0,0.333,0.667,1.0) mults (3,1,1,3) sum=8 → n_u=5 ✓;
    V knots (0.0,1.0,2.0) mults (3,1,3) sum=7 → n_v=4 ✓;
    V-domain [0,2] (not standard [0,1]); IS face surface;
    periodic U conversion → V-bounds check uses wrong [0,1] limit → mismatch.
  - C-1 DRIVER: V-domain scaled to [0,2]; post-periodicity-conversion V-bounds
    validator expects [0,1] → rejects valid V parameter.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn140",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V); "
        "5×4 control net; U_CLOSED=.T. (periodic U); "
        "U knots (0.0,0.333,0.667,1.0) mults (3,1,1,3) sum=8 → n_u=5; "
        "V knots (0.0,1.0,2.0) mults (3,1,3) sum=7 → n_v=4; "
        "V-domain [0,2] (non-unit); IS face surface; "
        "V-bounds check after periodic-U conversion applies wrong [0,1] limit → mismatch"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree-2 U × degree-2 V, 5×4 control net ──────
# U: n_u=5, p_u=2 → n_u+p_u+1=8. knots (0.0,0.333,0.667,1.0) mults (3,1,1,3) sum=8 ✓.
#    U_CLOSED=.T. for periodic topology.
# V: n_v=4, p_v=2 → n_v+p_v+1=7. knots (0.0,1.0,2.0) mults (3,1,3) sum=7 ✓.
#    V-domain is [0,2] to trigger the bounds mismatch.
# Control net: 4 V-rows × 5 U-cols; U-poles form a closed loop (first ≈ last).
r0 = [
    f.cartesian_point(( 1.0, 0.0, 0.0)),   # u=0, v=0
    f.cartesian_point(( 0.0, 1.0, 0.0)),   # u=0.333
    f.cartesian_point((-1.0, 0.0, 0.0)),   # u=0.5
    f.cartesian_point(( 0.0,-1.0, 0.0)),   # u=0.667
    f.cartesian_point(( 1.0, 0.0, 0.0)),   # u=1 (≡ u=0 periodic)
]
r1 = [
    f.cartesian_point(( 1.0, 0.0, 0.8)),
    f.cartesian_point(( 0.0, 1.0, 0.8)),
    f.cartesian_point((-1.0, 0.0, 0.8)),
    f.cartesian_point(( 0.0,-1.0, 0.8)),
    f.cartesian_point(( 1.0, 0.0, 0.8)),
]
r2 = [
    f.cartesian_point(( 1.0, 0.0, 1.6)),
    f.cartesian_point(( 0.0, 1.0, 1.6)),
    f.cartesian_point((-1.0, 0.0, 1.6)),
    f.cartesian_point(( 0.0,-1.0, 1.6)),
    f.cartesian_point(( 1.0, 0.0, 1.6)),
]
r3 = [
    f.cartesian_point(( 1.0, 0.0, 2.4)),
    f.cartesian_point(( 0.0, 1.0, 2.4)),
    f.cartesian_point((-1.0, 0.0, 2.4)),
    f.cartesian_point(( 0.0,-1.0, 2.4)),
    f.cartesian_point(( 1.0, 0.0, 2.4)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)},{row_ids(r3)})"

# U_CLOSED=.T., V-knots span [0,2]
mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn140_periodic_v_bounds',2,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.T.,.F.,.F.,"
    f"(3,1,1,3),(3,1,3),"
    f"(0.0,0.333,0.667,1.0),(0.0,1.0,2.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# Face occupies u∈[0,1] (full periodic wrap), v∈[0,2].
# 3D corners at seam: r0[0]=(1,0,0) and r3[0]=(1,0,2.4).
p_a3 = f.cartesian_point((1.0, 0.0, 0.0))
p_b3 = f.cartesian_point((1.0, 0.0, 2.4))
vt_a = f.vertex_point(p_a3)
vt_b = f.vertex_point(p_b3)

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

# Seam edge at u=0 (≡ u=1): v goes from 0 to 2 (z goes from 0 to 2.4).
e_seam_lo = mk_line_edge(vt_a, vt_b, (1.,0.,0.), (0.,0.,1.), (0.0,0.0), (0.,1.), 1.0)
e_seam_hi = mk_line_edge(vt_a, vt_b, (1.,0.,0.), (0.,0.,1.), (1.0,0.0), (0.,1.), 1.0)
# Bottom ring at v=0 (degenerate loop back to seam; use zero-length direction).
e_bot = mk_line_edge(vt_a, vt_a, (1.,0.,0.), (0.,0.,0.), (0.0,0.0), (1.,0.), 1.0)
# Top ring at v=2 (degenerate loop at z=2.4).
e_top = mk_line_edge(vt_b, vt_b, (1.,0.,2.4), (0.,0.,0.), (1.0,2.0), (-1.,0.), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e_seam_lo, True),
    f.oriented_edge(e_top,     True),
    f.oriented_edge(e_seam_hi, False),
    f.oriented_edge(e_bot,     False),
])
face  = f.advanced_face([f.face_outer_bound(loop)], mech_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
