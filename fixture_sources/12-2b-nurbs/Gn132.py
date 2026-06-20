"""Gn132 — Geom_BSplineCurve.IncreaseDegree weight-redistribution asymmetry.

Catalog claim: Rational B-spline curve degree 2, 4 poles with non-unit weights,
single interior knot. After IncreaseDegree(3), new poles/weights must preserve
curve shape and restore C2 continuity; asymmetric weight redistribution breaks
this.

STEP mechanism (literal):
  - RATIONAL_B_SPLINE_SURFACE + B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 1 (V).
    U-direction encodes the catalog curve: poles [(0,0,0),(1,2,0),(2,1,0),(3,0,0)],
    weights [1, 2, 1.5, 1], interior knot at 0.5.
    IS the face surface (mechanism IS the face surface).
  - C-1 DRIVER: non-unit weights at interior knot → IncreaseDegree weight
    redistribution asymmetry → shape deviation.

Mechanism vs driver:
  - CATALOG MECHANISM: RATIONAL_B_SPLINE_SURFACE + B_SPLINE_SURFACE_WITH_KNOTS
    degree=2 (U) × 1 (V); 4×2 control net; weights row0=(1,2,1.5,1)
    row1=(1,1,1,1); U mults (3,1,3) knots (0.0,0.5,1.0); V mults (2,2)
    knots (0.0,1.0); IS face surface; IncreaseDegree weight-redistribution
    asymmetry → shape deviation.
  - C-1 DRIVER: weights [1,2,1.5,1] at degree-2 interior knot → weight
    redistribution fails after degree elevation.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn132",
    defect=(
        "RATIONAL_B_SPLINE_SURFACE + B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 1 (V); "
        "4×2 control net; weights row0=(1,2,1.5,1) row1=(1,1,1,1); "
        "U mults (3,1,3) knots (0.0,0.5,1.0); V mults (2,2) knots (0.0,1.0); "
        "IS face surface; IncreaseDegree weight-redistribution asymmetry → shape deviation"
    ),
)

# ── CATALOG MECHANISM SURFACE: rational degree-2 U × degree-1 V, 4×2 net ──────
# U: n_u=4, p_u=2 → n_u+p_u+1=7. mults (3,1,3) → sum=7 ✓. knots (0.0,0.5,1.0).
# V: n_v=2, p_v=1 → n_v+p_v+1=4. mults (2,2) → sum=4 ✓. knots (0.0,1.0).
# Poles: catalog curve at Z=0 (row0) extruded to Z=1 (row1).
r0 = [
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.cartesian_point((1.0, 2.0, 0.0)),
    f.cartesian_point((2.0, 1.0, 0.0)),
    f.cartesian_point((3.0, 0.0, 0.0)),
]
r1 = [
    f.cartesian_point((0.0, 0.0, 1.0)),
    f.cartesian_point((1.0, 2.0, 1.0)),
    f.cartesian_point((2.0, 1.0, 1.0)),
    f.cartesian_point((3.0, 0.0, 1.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)})"

# Weights: STEP order V-outer, U-inner.
# row0 (V=0): weights from catalog = (1, 2, 1.5, 1)
# row1 (V=1): all 1.0 (neutral extrusion)
w_r0 = "(1.0,2.0,1.5,1.0)"
w_r1 = "(1.0,1.0,1.0,1.0)"
weights = f"({w_r0},{w_r1})"

mech_surf = f._emit_raw(
    f"(RATIONAL_B_SPLINE_SURFACE({weights})"
    f"B_SPLINE_SURFACE('gn132_weight_asym',2,1,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.)"
    f"B_SPLINE_SURFACE_WITH_KNOTS((3,1,3),(2,2),"
    f"(0.0,0.5,1.0),(0.0,1.0),.UNSPECIFIED.)"
    f"GEOMETRIC_REPRESENTATION_ITEM()"
    f"REPRESENTATION_ITEM('gn132_surf'))"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# 3D corners: r0[0]=(0,0,0), r0[3]=(3,0,0), r1[3]=(3,0,1), r1[0]=(0,0,1).
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((3.0, 0.0, 0.0))
p_c3 = f.cartesian_point((3.0, 0.0, 1.0))
p_d3 = f.cartesian_point((0.0, 0.0, 1.0))
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

# UV: U∈[0,1], V∈[0,1]. 3D U-direction maps to x=0..3, V to z=0..1.
e_bot   = mk_line_edge(vt_a, vt_b, (0.,0.,0.),  (1.,0.,0.),  (0.0,0.0), (1.,0.), 1.0)
e_right = mk_line_edge(vt_b, vt_c, (3.,0.,0.),  (0.,0.,1.),  (1.0,0.0), (0.,1.), 1.0)
e_top   = mk_line_edge(vt_c, vt_d, (3.,0.,1.),  (-1.,0.,0.), (1.0,1.0), (-1.,0.), 1.0)
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
