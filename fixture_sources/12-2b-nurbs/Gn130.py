"""Gn130 — ShapeUpgrade_ConvertCurveToBezier non-uniform-knots tail-degenerate.

Catalog claim: 2D B-spline curve, degree 3, with non-uniform knots where the
last segment is nearly degenerate (poles 4 and 5 very close together).
ShapeUpgrade_ConvertCurveToBezier::Perform() produces a tail Bezier patch
that degenerates to near-zero length, causing downstream failure.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree 3 (U) × 1 (V), with the U-direction
    curve matching the catalog: poles at U=0..4 spaced normally, then a
    compressed tail at U≈4 (poles[4]=(4,4,0) and poles[5]=(4.01,4.01,0)).
    Knots non-uniform: [0,0,0,0, 0.2, 0.25, 0.5, 0.75, 1,1,1,1].
    The nearly-equal last two poles produce a near-degenerate Bezier tail
    segment after ConvertCurveToBezier; the tail patch collapses.
    IS the face surface (mechanism IS the face surface).
  - C-1 DRIVER: near-coincident tail poles + non-uniform knots → degenerate
    tail Bezier patch → conversion failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=3 (U) × 1 (V);
    U-direction poles [(0,0),(1,2),(2,1),(3,3),(4,4),(4.01,4.01)] (6 poles);
    U knots (0,0,0,0,0.2,0.25,0.5,0.75,1,1,1,1) non-uniform; V mults (2,2)
    knots (0.0,1.0); IS face surface;
    ConvertCurveToBezier tail degeneracy → conversion failure.
  - C-1 DRIVER: near-coincident poles[4]/poles[5] → degenerate tail Bezier.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn130",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=3 (U) × 1 (V); "
        "U poles (0,0,0)(1,2,0)(2,1,0)(3,3,0)(4,4,0)(4.01,4.01,0) 6 poles; "
        "U knots (0,0,0,0,0.2,0.25,0.5,0.75,1,1,1,1) non-uniform; "
        "V mults (2,2) knots (0.0,1.0); IS face surface; "
        "ConvertCurveToBezier near-coincident tail poles → degenerate tail Bezier"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree-3 U × degree-1 V, 6×2 control net ──────
# U: n_u=6, p_u=3 → n_u+p_u+1=10. knots non-uniform with mults
#    (4,1,1,1,1,4) → sum=12... too many.
#    Catalog knots: [0,0,0,0, 0.2, 0.25, 0.5, 0.75, 1,1,1,1] → 12 values.
#    Distinct knots: (0.0, 0.2, 0.25, 0.5, 0.75, 1.0) mults (4,1,1,1,1,4) sum=12.
#    But n_u+p_u+1 must = 12 → n_u = 8. Use 8 U-columns (extend poles).
#    Actually: catalog says poles = 6, knots 12 values → n_u+p_u+1 = n_u+4 = 12 → n_u=8.
#    Extend poles to 8: add two more in the degenerate tail region.
# V: n_v=2, p_v=1 → n_v+p_v+1=4. mults (2,2) → sum=4 ✓. knots (0.0,1.0).
#
# U poles (8): (0,0,0),(1,2,0),(2,1,0),(3,3,0),(4,4,0),(4.01,4.01,0),(4.02,4.02,0),(4.03,4.03,0)
# — the last 4 poles cluster near (4,4,0) producing a degenerate tail.
# Extrude in Z for the V direction.
u_row0 = [
    f.cartesian_point((0.00, 0.00, 0.0)),
    f.cartesian_point((1.00, 2.00, 0.0)),
    f.cartesian_point((2.00, 1.00, 0.0)),
    f.cartesian_point((3.00, 3.00, 0.0)),
    f.cartesian_point((4.00, 4.00, 0.0)),
    f.cartesian_point((4.01, 4.01, 0.0)),
    f.cartesian_point((4.02, 4.02, 0.0)),
    f.cartesian_point((4.03, 4.03, 0.0)),
]
u_row1 = [
    f.cartesian_point((0.00, 0.00, 1.0)),
    f.cartesian_point((1.00, 2.00, 1.0)),
    f.cartesian_point((2.00, 1.00, 1.0)),
    f.cartesian_point((3.00, 3.00, 1.0)),
    f.cartesian_point((4.00, 4.00, 1.0)),
    f.cartesian_point((4.01, 4.01, 1.0)),
    f.cartesian_point((4.02, 4.02, 1.0)),
    f.cartesian_point((4.03, 4.03, 1.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(u_row0)},{row_ids(u_row1)})"

# U: 8 poles, degree 3 → sum=12. mults (4,1,1,1,1,4) → sum=12 ✓.
# V: 2 poles, degree 1 → sum=4.  mults (2,2) → sum=4 ✓.
mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn130_tail_degenerate',3,1,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,1,1,1,1,4),(2,2),"
    f"(0.0,0.2,0.25,0.5,0.75,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# UV domain: U ∈ [0,1], V ∈ [0,1].
# 3D corners: u_row0[0]=(0,0,0), u_row0[7]=(4.03,4.03,0),
#             u_row1[0]=(0,0,1),  u_row1[7]=(4.03,4.03,1).
p_a3 = f.cartesian_point((0.00, 0.00, 0.0))
p_b3 = f.cartesian_point((4.03, 4.03, 0.0))
p_c3 = f.cartesian_point((4.03, 4.03, 1.0))
p_d3 = f.cartesian_point((0.00, 0.00, 1.0))
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

# V=0 bottom (U: 0→1 param → 3D diagonal), U=1 right (V: 0→1 → Z extrusion),
# V=1 top (U: 1→0), U=0 left (V: 1→0).
e_bot   = mk_line_edge(vt_a, vt_b, (0.,0.,0.),    (1.,1.,0.),  (0.0,0.0), (1.,0.), 1.0)
e_right = mk_line_edge(vt_b, vt_c, (4.03,4.03,0.),(0.,0.,1.),  (1.0,0.0), (0.,1.), 1.0)
e_top   = mk_line_edge(vt_c, vt_d, (4.03,4.03,1.),(-1.,-1.,0.),(1.0,1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(vt_d, vt_a, (0.,0.,1.),    (0.,0.,-1.), (0.0,1.0), (0.,-1.), 1.0)

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
