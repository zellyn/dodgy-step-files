"""Gn117 — ShapeUpgrade_SplitSurface with-rational-and-non-rational-mixed.

Catalog claim: Rational B-spline surface (degree 2×1) with mixed rationality:
weights specified (rational in U) but V direction non-rational. Init's split
logic assumes uniform rationality and produces incorrect patch boundaries.

STEP mechanism (literal):
  - RATIONAL_B_SPLINE_SURFACE + B_SPLINE_SURFACE_WITH_KNOTS (complex entity)
    degree 2 (U) × 1 (V), 3×2 control net.
    U: n=3, p=2 → n+p+1=6. mults (3,3) knots (0.0,1.0) sum=6 ✓.
    V: m=2, p=1 → m+p+1=4. mults (2,2) knots (0.0,1.0) sum=4 ✓.
    Weights: row 0 = (1.0, 0.707, 1.0), row 1 = (1.0, 0.707, 1.0).
    Non-unit weights in U create a rational surface; V has equal weights
    (all 1.0 within each row) so V direction is effectively non-rational.
    SplitSurface.Init assumes either fully rational or fully non-rational
    and applies one code path for both directions; the mixed state causes
    incorrect patch boundary computation.
    IS the face surface (mechanism IS the face surface).
  - C-1 DRIVER: mixed rationality → Init patch boundary mismatch → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: RATIONAL_B_SPLINE_SURFACE + B_SPLINE_SURFACE_WITH_KNOTS
    degree=2 (U) × 1 (V); 3×2 control net; U mults (3,3) sum=6 ✓;
    V mults (2,2) sum=4 ✓; weights (1.0,0.707,1.0) per row (rational in U,
    non-rational in V); IS face surface;
    SplitSurface.Init uniform-rationality assumption violated → shape_null=True.
  - C-1 DRIVER: mixed rationality → incorrect patch boundaries → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn117",
    defect=(
        "RATIONAL_B_SPLINE_SURFACE+B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 1 (V); "
        "3×2 control net; U mults (3,3) sum=6 ✓; V mults (2,2) sum=4 ✓; "
        "weights (1.0,0.707,1.0) per row (rational in U, non-rational in V); "
        "IS face surface; "
        "SplitSurface.Init uniform-rationality assumption violated → shape_null=True"
    ),
)

# ── CATALOG MECHANISM SURFACE: rational (U) + non-rational (V) B-spline surface ─
# Degree 2 in U, degree 1 in V. 3×2 control net (v=0 row, v=1 row).
# U: n=3, p=2 → n+p+1=6. mults (3,3) knots (0.0,1.0) sum=6 ✓.
# V: m=2, p=1 → m+p+1=4. mults (2,2) knots (0.0,1.0) sum=4 ✓.
# Weights: middle U pole has w=0.707 (=1/√2) → rational quarter-circle arc in U.
# V weights all equal 1.0 → non-rational (linear) in V.
# net[v][u]: v=0 at y=0, v=1 at y=5.
r0 = [
    f.cartesian_point((0.0, 0.0, 0.0)),   # u=0
    f.cartesian_point((1.0, 0.0, 1.0)),   # u=1 (middle CP, lifted to create arc)
    f.cartesian_point((2.0, 0.0, 0.0)),   # u=2
]
r1 = [
    f.cartesian_point((0.0, 5.0, 0.0)),
    f.cartesian_point((1.0, 5.0, 1.0)),
    f.cartesian_point((2.0, 5.0, 0.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)})"

# Weights: 2 rows of 3. Middle pole weight = 0.707 (rational in U).
# V weights both 1.0 → non-rational in V.
weights_net = "((1.0,0.707,1.0),(1.0,0.707,1.0))"

# Complex entity: RATIONAL_B_SPLINE_SURFACE + B_SPLINE_SURFACE_WITH_KNOTS.
mech_surf = f._emit_raw(
    f"(B_SPLINE_SURFACE(2,1,{cp_net},.UNSPECIFIED.,.F.,.F.,.F.)"
    f"B_SPLINE_SURFACE_WITH_KNOTS("
    f"(3,3),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
    f"GEOMETRIC_REPRESENTATION_ITEM()"
    f"RATIONAL_B_SPLINE_SURFACE({weights_net})"
    f"REPRESENTATION_ITEM('gn117_mixed_rational_surf')"
    f"SURFACE())"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Edges on the surface boundary (UV corners) ───────────────────────────────
# Surface domain: U ∈ [0,1], V ∈ [0,1].
# 3D corners: r0[0]=(0,0,0), r0[2]=(2,0,0), r1[0]=(0,5,0), r1[2]=(2,5,0).
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((2.0, 0.0, 0.0))
p_c3 = f.cartesian_point((2.0, 5.0, 0.0))
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

# Bottom: v=0 boundary, U from 0→1
e_bot   = mk_line_edge(v_a, v_b, (0.0,0.0,0.0), (1.,0.,0.), (0.0,0.0), (1.,0.), 2.0)
# Right: u=1 boundary, V from 0→1
e_right = mk_line_edge(v_b, v_c, (2.0,0.0,0.0), (0.,1.,0.), (1.0,0.0), (0.,1.), 5.0)
# Top: v=1 boundary, U from 1→0
e_top   = mk_line_edge(v_c, v_d, (2.0,5.0,0.0), (-1.,0.,0.), (1.0,1.0), (-1.,0.), 2.0)
# Left: u=0 boundary, V from 1→0
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
