"""Gn115 — ShapeUpgrade_ConvertSurfaceToBezierBasis non-uniform-degree.

Catalog claim: B-spline surface with highly disparate degrees: U direction
degree 5, V direction degree 1. Control point layout (7×2) creates vastly
different patch sizes when converted to Bezier basis. Tests Init's assumption
of uniform degree across dimensions.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree 5 (U) × 1 (V), 7×2 control net.
    U: n=7, p=5 → n+p+1=13. mults (6,1,6) knots (0.0,0.5,1.0) sum=13 ✓.
    V: m=2, p=1 → m+p+1=4. mults (2,2) knots (0.0,1.0) sum=4 ✓.
    Degree 5 in U vs degree 1 in V: hugely disparate. ConvertSurfaceToBezierBasis
    breaks U into patches (Bezier degree-5 patches) and V into patches (degree-1
    segments); the assumption that both directions produce compatible patch sizes
    fails → shape_null=True.
    IS the face surface (mechanism IS the face surface).
  - C-1 DRIVER: disparate degree Bezier decomposition produces incompatible
    patch boundaries → shape processing rejects → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=5 (U) × 1 (V);
    7×2 control net; U mults (6,1,6) knots (0.0,0.5,1.0) sum=13 ✓;
    V mults (2,2) knots (0.0,1.0) sum=4 ✓;
    IS face surface;
    ConvertSurfaceToBezierBasis uniform-degree assumption violated → shape_null=True.
  - C-1 DRIVER: disparate Bezier patch sizes → boundary mismatch → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn115",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=5 (U) × 1 (V); 7×2 control net; "
        "U mults (6,1,6) knots (0.0,0.5,1.0) sum=13 ✓; "
        "V mults (2,2) knots (0.0,1.0) sum=4 ✓; "
        "IS face surface; "
        "ConvertSurfaceToBezierBasis uniform-degree assumption violated "
        "(degree 5 vs 1) → incompatible patch sizes → shape_null=True"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree 5 × 1 B-spline surface ─────────────────
# U: 7 control points, degree 5. n=7, p=5 → n+p+1=13.
#   U mults (6,1,6) knots (0.0,0.5,1.0) sum=13 ✓.
#   Interior knot at u=0.5 with mult=1 (C4 continuity): one Bezier patch each side.
# V: 2 control points, degree 1. m=2, p=1 → m+p+1=4.
#   V mults (2,2) knots (0.0,1.0) sum=4 ✓. Single linear patch in V.
# Control net: 7 (U) × 2 (V) = 14 points.
# Convention: net[v][u], i.e., 2 rows (v=0 and v=1) of 7 columns (u=0..6).
r0 = [
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.cartesian_point((1.0, 0.2, 0.0)),
    f.cartesian_point((2.0, 0.8, 0.0)),
    f.cartesian_point((3.0, 1.0, 0.0)),
    f.cartesian_point((4.0, 0.8, 0.0)),
    f.cartesian_point((5.0, 0.2, 0.0)),
    f.cartesian_point((6.0, 0.0, 0.0)),
]
r1 = [
    f.cartesian_point((0.0, 5.0, 0.0)),
    f.cartesian_point((1.0, 5.2, 0.0)),
    f.cartesian_point((2.0, 5.8, 0.0)),
    f.cartesian_point((3.0, 6.0, 0.0)),
    f.cartesian_point((4.0, 5.8, 0.0)),
    f.cartesian_point((5.0, 5.2, 0.0)),
    f.cartesian_point((6.0, 5.0, 0.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)})"

mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn115_deg5x1_surf',5,1,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(6,1,6),(2,2),"
    f"(0.0,0.5,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Edges on the surface (corners at UV corners of the surface domain) ─────────
# Surface domain: U ∈ [0,1], V ∈ [0,1] (parametric).
# Corner 3D points: r0[0], r0[6], r1[0], r1[6].
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((6.0, 0.0, 0.0))
p_c3 = f.cartesian_point((6.0, 5.0, 0.0))
p_d3 = f.cartesian_point((0.0, 5.0, 0.0))
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

# Bottom: v=0 edge, U from 0→1 (3D from (0,0,0)→(6,0,0))
e_bot   = mk_line_edge(v_a, v_b, (0.0,0.0,0.0), (1.,0.,0.), (0.0,0.0), (1.,0.), 6.0)
# Right: u=1 edge, V from 0→1 (3D from (6,0,0)→(6,5,0))
e_right = mk_line_edge(v_b, v_c, (6.0,0.0,0.0), (0.,1.,0.), (1.0,0.0), (0.,1.), 5.0)
# Top: v=1 edge, U from 1→0 (3D from (6,5,0)→(0,5,0))
e_top   = mk_line_edge(v_c, v_d, (6.0,5.0,0.0), (-1.,0.,0.), (1.0,1.0), (-1.,0.), 6.0)
# Left: u=0 edge, V from 1→0 (3D from (0,5,0)→(0,0,0))
e_left  = mk_line_edge(v_d, v_a, (0.0,5.0,0.0), (0.,-1.,0.), (0.0,1.0), (0.,-1.), 5.0)

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
