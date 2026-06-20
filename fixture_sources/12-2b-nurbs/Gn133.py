"""Gn133 — ShapeAnalysis_Curve.CheckOffsetCurve knot-ratio-overflow degenerate-segment.

Catalog claim: B-spline curve degree 3, 9 poles, with geometry concentrated in
[0, 0.01] and [0.5, 0.51], and sparse in between. Knot vector clusters at both
ends of the dense regions. When CheckOffsetCurve is called with offset=0.1, the
short dense segments produce knot ratios that overflow, exposing a degenerate
segment.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree=3 (U) × 1 (V), 9×2 control net.
    U-direction encodes the catalog curve: dense clusters at U≈0 and U≈0.5,
    sparse middle. IS the face surface (mechanism IS the face surface).
  - C-1 DRIVER: extreme knot spacing ratios (dense vs sparse segments) →
    knot-ratio overflow in CheckOffsetCurve → degenerate segment detection.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=3 (U) × 1 (V);
    9×2 control net; U knots (0,0,0,0, 0.01, 0.5, 0.51, 1, 1, 1, 1, 1)
    mults (4,1,1,1,1,4); V mults (2,2) knots (0.0,1.0); IS face surface;
    CheckOffsetCurve knot-ratio-overflow → degenerate-segment failure.
  - C-1 DRIVER: clustered knots at 0.01 and 0.5..0.51 → extreme ratio → overflow.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn133",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=3 (U) × 1 (V); "
        "9×2 control net; poles clustered near u=0 and u=0.5; "
        "U knots (0,0,0,0,0.01,0.5,0.51,1,1,1,1,1) mults (4,1,1,1,1,4); "
        "V mults (2,2) knots (0.0,1.0); IS face surface; "
        "CheckOffsetCurve knot-ratio-overflow → degenerate-segment"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree-3 U × degree-1 V, 9×2 control net ──────
# U: n_u=9, p_u=3 → n_u+p_u+1=13. knots: (0,0.01,0.5,0.51,1) mults (4,1,1,1,4) sum=11≠13.
# Need sum=13. Use mults (4,1,1,1,2,4) → sum=13 with knots (0,0.01,0.5,0.51,0.75,1.0):
#   9 distinct knot spans → n_u+1 = 9 → n_u=9. But n_u+p_u+1=13 → knot sum=13 ✓.
#   Knots: (0.0, 0.01, 0.5, 0.51, 0.75, 1.0), mults (4,1,1,1,2,4) sum=13 ✓.
# V: n_v=2, p_v=1 → n_v+p_v+1=4. mults (2,2) → sum=4 ✓. knots (0.0,1.0).
#
# Poles encode geometry concentrated near x≈0 (u_param≈0) and x≈5 (u_param≈0.5),
# sparse between and after.
u_row0 = [
    f.cartesian_point((0.00, 0.00, 0.0)),   # u≈0 dense start
    f.cartesian_point((0.10, 0.05, 0.0)),   # u≈0.01 dense end
    f.cartesian_point((1.00, 0.20, 0.0)),   # sparse middle
    f.cartesian_point((2.00, 0.30, 0.0)),   # sparse
    f.cartesian_point((5.00, 0.50, 0.0)),   # u≈0.5 dense start
    f.cartesian_point((5.10, 0.45, 0.0)),   # u≈0.51 dense end
    f.cartesian_point((6.00, 0.30, 0.0)),   # sparse
    f.cartesian_point((8.00, 0.10, 0.0)),   # u≈0.75
    f.cartesian_point((10.0, 0.00, 0.0)),   # u=1
]
u_row1 = [
    f.cartesian_point((0.00, 0.00, 1.0)),
    f.cartesian_point((0.10, 0.05, 1.0)),
    f.cartesian_point((1.00, 0.20, 1.0)),
    f.cartesian_point((2.00, 0.30, 1.0)),
    f.cartesian_point((5.00, 0.50, 1.0)),
    f.cartesian_point((5.10, 0.45, 1.0)),
    f.cartesian_point((6.00, 0.30, 1.0)),
    f.cartesian_point((8.00, 0.10, 1.0)),
    f.cartesian_point((10.0, 0.00, 1.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(u_row0)},{row_ids(u_row1)})"

mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn133_knot_ratio',3,1,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,1,1,1,2,4),(2,2),"
    f"(0.0,0.01,0.5,0.51,0.75,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# 3D corners: row0[0]=(0,0,0), row0[8]=(10,0,0), row1[8]=(10,0,1), row1[0]=(0,0,1).
p_a3 = f.cartesian_point((0.0,  0.0, 0.0))
p_b3 = f.cartesian_point((10.0, 0.0, 0.0))
p_c3 = f.cartesian_point((10.0, 0.0, 1.0))
p_d3 = f.cartesian_point((0.0,  0.0, 1.0))
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

# UV domain U∈[0,1] V∈[0,1]; 3D: x=0..10 at y=0, z=0..1.
e_bot   = mk_line_edge(vt_a, vt_b, (0.,0.,0.),  (1.,0.,0.),  (0.0,0.0), (1.,0.), 1.0)
e_right = mk_line_edge(vt_b, vt_c, (10.,0.,0.), (0.,0.,1.),  (1.0,0.0), (0.,1.), 1.0)
e_top   = mk_line_edge(vt_c, vt_d, (10.,0.,1.), (-1.,0.,0.), (1.0,1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(vt_d, vt_a, (0.,0.,1.),  (0.,0.,-1.), (0.0,1.0), (0.,-1.), 1.0)

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
