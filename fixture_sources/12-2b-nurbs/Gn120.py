"""Gn120 — ShapeUpgrade_ConvertSurfaceToBezierBasis with-clamped-knots-degenerate.

Catalog claim: B-spline surface, degree (2,2), where U-direction knots are
clamped (multiplicity at endpoints = degree+1 = 3) but V-direction knots are
unclamped (interior only, no endpoint repetition). Conversion to Bezier basis
applies different logic per direction, causing inconsistent patch decomposition.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree 2 (U) × 2 (V), 4×2 control net.
    Wait: for degree-2 surface with mults, we need control net sizes consistent.
    U: n_u=4, p_u=2 → n_u+p_u+1=7. clamped mults (3,1,3) knots (0.0,0.5,1.0)
    sum=7 ✓.
    V: n_v=2, p_v=2 → n_v+p_v+1=5. unclamped mults (1,1,1) won't work —
    need sum=5. Use mults (2,1,2) knots (0.1,0.5,0.9) — but these don't
    reach 0 or 1 (unclamped). sum=5 ✓.
    The U direction is clamped (interpolates corners), V is unclamped
    (floating domain). ConvertSurfaceToBezierBasis applies clamped-knot
    Bezier extraction to U and unclamped logic to V; the inconsistency
    produces incorrect patch boundaries → shape_null=True.
    IS the face surface (mechanism IS the face surface).
  - C-1 DRIVER: clamped U / unclamped V → inconsistent Bezier conversion
    → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V);
    4×2 control net; U mults (3,1,3) knots (0.0,0.5,1.0) sum=7 ✓ (clamped);
    V mults (2,1,2) knots (0.1,0.5,0.9) sum=5 ✓ (unclamped — no 0 or 1);
    IS face surface;
    ConvertSurfaceToBezierBasis inconsistent per-direction logic → shape_null=True.
  - C-1 DRIVER: mixed clamped/unclamped knot vectors → incorrect Bezier patches
    → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn120",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V); 4×2 control net; "
        "U mults (3,1,3) knots (0.0,0.5,1.0) sum=7 ✓ (clamped); "
        "V mults (2,1,2) knots (0.1,0.5,0.9) sum=5 ✓ (unclamped); "
        "IS face surface; "
        "ConvertSurfaceToBezierBasis inconsistent per-direction logic → shape_null=True"
    ),
)

# ── CATALOG MECHANISM SURFACE: clamped-U / unclamped-V B-spline surface ──────
# Degree 2 in U and V. 4×2 control net (4 cols in U, 2 rows in V).
# U: n_u=4, p_u=2 → sum=7. mults (3,1,3) knots (0.0,0.5,1.0) ✓.
# V: n_v=2, p_v=2 → sum=5. mults (2,1,2) knots (0.1,0.5,0.9) ✓ (unclamped).
# net[v][u]: v=0 row at z=0, v=1 row at z=3.
r0 = [
    f.cartesian_point((0.0, 0.0, 0.0)),   # u=0
    f.cartesian_point((1.0, 0.5, 0.0)),   # u=1
    f.cartesian_point((2.0, 0.5, 0.0)),   # u=2
    f.cartesian_point((3.0, 0.0, 0.0)),   # u=3
]
r1 = [
    f.cartesian_point((0.0, 0.0, 3.0)),
    f.cartesian_point((1.0, 0.5, 3.0)),
    f.cartesian_point((2.0, 0.5, 3.0)),
    f.cartesian_point((3.0, 0.0, 3.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)})"

mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn120_clamped_u_unclamped_v',2,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,1,3),(2,1,2),"
    f"(0.0,0.5,1.0),(0.1,0.5,0.9),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Edges on the surface boundary ────────────────────────────────────────────
# 3D corners: r0[0]=(0,0,0), r0[3]=(3,0,0), r1[0]=(0,0,3), r1[3]=(3,0,3).
# UV domain: U ∈ [0,1], V ∈ [0.1,0.9] (unclamped V domain).
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((3.0, 0.0, 0.0))
p_c3 = f.cartesian_point((3.0, 0.0, 3.0))
p_d3 = f.cartesian_point((0.0, 0.0, 3.0))
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

# Bottom: v=0.1 boundary, U from 0→1
e_bot   = mk_line_edge(v_a, v_b, (0.0,0.0,0.0), (1.,0.,0.), (0.0,0.1), (1.,0.), 3.0)
# Right: u=1 boundary, V from 0.1→0.9
e_right = mk_line_edge(v_b, v_c, (3.0,0.0,0.0), (0.,0.,1.), (1.0,0.1), (0.,1.), 3.0)
# Top: v=0.9 boundary, U from 1→0
e_top   = mk_line_edge(v_c, v_d, (3.0,0.0,3.0), (-1.,0.,0.), (1.0,0.9), (-1.,0.), 3.0)
# Left: u=0 boundary, V from 0.9→0.1
e_left  = mk_line_edge(v_d, v_a, (0.0,0.0,3.0), (0.,0.,-1.), (0.0,0.9), (0.,-1.), 3.0)

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
