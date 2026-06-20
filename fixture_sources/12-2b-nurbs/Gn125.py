"""Gn125 — ShapeUpgrade_SplitSurface.SetVSplitValues partial-domain.

Catalog claim: BSpline surface with full V domain [0,1]. Split values provided
only for partial range [0.3, 0.7]. SetVSplitValues clips silently, leaving V
ranges [0, 0.3) and (0.7, 1] unprocessed and unsplit.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree 3 (U) × 3 (V), 4×4 control net,
    full V domain [0,1]. SetVSplitValues([0.3, 0.7]) supplies split knots
    only in the interior partial range. The surface boundary edges live at
    V=0 and V=1; the split logic never visits those outer bands.
    Downstream patch assembly assumes all V subdomains were split and finds
    the outer bands absent → shape_null=True.
    IS the face surface (mechanism IS the face surface).
  - C-1 DRIVER: partial-domain V split → outer bands [0,0.3) and (0.7,1]
    unprocessed → patch assembly failure → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=3 (U) × 3 (V);
    4×4 control net; U mults (4,4) knots (0.0,1.0); V mults (4,4) knots
    (0.0,1.0); IS face surface;
    SetVSplitValues([0.3,0.7]) partial-domain → outer bands unsplit
    → shape_null=True.
  - C-1 DRIVER: partial V split values → outer band loss → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn125",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=3 (U) × 3 (V); 4×4 control net; "
        "U mults (4,4) knots (0.0,1.0); V mults (4,4) knots (0.0,1.0); "
        "IS face surface; "
        "SetVSplitValues([0.3,0.7]) partial-domain → outer bands [0,0.3) (0.7,1] unsplit "
        "→ patch assembly failure → shape_null=True"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree-3 B-spline, full V domain [0,1] ────────
# 4×4 control net; U and V both fully clamped (mults=4 at ends).
# Split values only cover [0.3, 0.7] — outer bands unseen by splitter.
r0 = [f.cartesian_point((i, 0.0, 0.0)) for i in range(4)]
r1 = [f.cartesian_point((i, 1.0, 1.0)) for i in range(4)]
r2 = [f.cartesian_point((i, 2.0, 1.0)) for i in range(4)]
r3 = [f.cartesian_point((i, 3.0, 0.0)) for i in range(4)]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)},{row_ids(r3)})"

mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn125_partial_v_split',3,3,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,4),(4,4),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges on the surface ─────────────────────────────────────────────
# 3D corners: r0[0]=(0,0,0), r0[3]=(3,0,0), r3[0]=(0,3,0), r3[3]=(3,3,0).
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((3.0, 0.0, 0.0))
p_c3 = f.cartesian_point((3.0, 3.0, 0.0))
p_d3 = f.cartesian_point((0.0, 3.0, 0.0))
v_a = f.vertex_point(p_a3)
v_b = f.vertex_point(p_b3)
v_c = f.vertex_point(p_c3)
v_d = f.vertex_point(p_d3)

def mk_line_edge(vs_, ve_, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
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

# V=0 boundary (U: 0→1), V=1 boundary (U: 1→0), U=1 right, U=0 left.
e_bot   = mk_line_edge(v_a, v_b, (0.,0.,0.), (1.,0.,0.), (0.0,0.0), (1.,0.), 3.0)
e_right = mk_line_edge(v_b, v_c, (3.,0.,0.), (0.,1.,0.), (1.0,0.0), (0.,1.), 3.0)
e_top   = mk_line_edge(v_c, v_d, (3.,3.,0.), (-1.,0.,0.),(1.0,1.0), (-1.,0.), 3.0)
e_left  = mk_line_edge(v_d, v_a, (0.,3.,0.), (0.,-1.,0.),(0.0,1.0), (0.,-1.), 3.0)

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
