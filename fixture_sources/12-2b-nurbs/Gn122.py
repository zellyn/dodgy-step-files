"""Gn122 — ShapeUpgrade_SplitSurface.Init with-control-net-collapsed.

Catalog claim: B-spline surface whose first 6 control points map to a single
location (1,1,1); remaining 2 points at (2,2,2). Split initialization logic
skips validation of degenerate control nets, allowing the invalid surface to
proceed to the splitting algorithm.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree (2,2), 4×2 control net = 8 CPs total.
    U: n_u=4, p_u=2 → n_u+p_u+1=7. mults (3,1,3) knots (0.0,0.5,1.0) sum=7 ✓.
    V: n_v=2, p_v=2 → n_v+p_v+1=5. mults (3,3) knots (0.0,1.0) sum=5 — wait
    need sum=5. mults (3,2) won't give 5 correctly. n_v=2 means 2 poles in V,
    so V knot vector: p_v+1=3 mults at start + 1 interior needed for n=4?
    Actually with n_v=2, we need m_v+1 = n_v + p_v + 1 = 5 knots total.
    mults (3,2) knots (0.0,1.0) → sum=5 ✓ (no interior knots in V).
    net[v][u] = 4 poles per row, 2 rows.
    First row (v=0): all 4 poles at (1,1,1) → collapsed.
    Second row (v=1): poles 0,1 at (1,1,1), poles 2,3 at (2,2,2).
    Total 6 poles at (1,1,1), 2 at (2,2,2).
    SplitSurface.Init proceeds without degenerate net check → shape_null=True.
    IS the face surface (mechanism IS the face surface).
  - C-1 DRIVER: collapsed control net → SplitSurface.Init skips degenerate
    validation → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V);
    4×2 control net; U mults (3,1,3) knots (0.0,0.5,1.0) sum=7 ✓;
    V mults (3,2) knots (0.0,1.0) sum=5 ✓;
    first 6 CPs at (1,1,1); last 2 at (2,2,2);
    IS face surface;
    SplitSurface.Init skips degenerate-net check → shape_null=True.
  - C-1 DRIVER: 6/8 CPs collapsed to single point → degenerate surface
    reaches splitting algorithm → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn122",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V); 4×2 control net; "
        "U mults (3,1,3) knots (0.0,0.5,1.0) sum=7 ✓; "
        "V mults (3,2) knots (0.0,1.0) sum=5 ✓; "
        "6/8 CPs at (1,1,1) collapsed; 2 CPs at (2,2,2); "
        "IS face surface; "
        "SplitSurface.Init skips degenerate-net check → shape_null=True"
    ),
)

# ── CATALOG MECHANISM SURFACE: collapsed control net B-spline surface ─────────
# Degree 2 in U and V. 4×2 control net (4 cols in U, 2 rows in V).
# U: n_u=4, p_u=2 → sum=7. mults (3,1,3) knots (0.0,0.5,1.0) ✓.
# V: n_v=2, p_v=2 → sum=5. mults (3,2) knots (0.0,1.0) ✓ (no interior V knot).
# row v=0: all 4 poles at (1,1,1) → degenerate first row.
# row v=1: poles u=0,u=1 at (1,1,1); poles u=2,u=3 at (2,2,2).
# Total: 6 at (1,1,1), 2 at (2,2,2).

# row 0: all collapsed
r0_cp = [(1.0, 1.0, 1.0)] * 4
r0 = [f.cartesian_point(p) for p in r0_cp]

# row 1: first 2 collapsed, last 2 at offset
r1 = [
    f.cartesian_point((1.0, 1.0, 1.0)),
    f.cartesian_point((1.0, 1.0, 1.0)),
    f.cartesian_point((2.0, 2.0, 2.0)),
    f.cartesian_point((2.0, 2.0, 2.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)})"

mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn122_collapsed_net',2,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,1,3),(3,2),"
    f"(0.0,0.5,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Edges bounding the face using the collapsed surface ───────────────────────
# Since the surface is degenerate (collapsed near (1,1,1)), we define nominal
# 3D corner geometry that corresponds to the surface UV domain corners.
# UV domain: U ∈ [0,1], V ∈ [0,1]. We use a small bounding box near (1,1,1).
p_a3 = f.cartesian_point((1.0, 1.0, 1.0))   # (u=0,v=0) → collapsed
p_b3 = f.cartesian_point((2.0, 1.0, 1.0))   # (u=1,v=0) → also collapsed (nom.)
p_c3 = f.cartesian_point((2.0, 2.0, 2.0))   # (u=1,v=1) → offset region
p_d3 = f.cartesian_point((1.0, 2.0, 2.0))   # (u=0,v=1) → collapsed/offset
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

# Bottom: v=0, U from 0→1
e_bot   = mk_line_edge(v_a, v_b, (1.0,1.0,1.0), (1.,0.,0.), (0.0,0.0), (1.,0.), 1.0)
# Right: u=1, V from 0→1
e_right = mk_line_edge(v_b, v_c, (2.0,1.0,1.0), (0.,1.,1.), (1.0,0.0), (0.,1.), 1.414)
# Top: v=1, U from 1→0
e_top   = mk_line_edge(v_c, v_d, (2.0,2.0,2.0), (-1.,0.,0.), (1.0,1.0), (-1.,0.), 1.0)
# Left: u=0, V from 1→0
e_left  = mk_line_edge(v_d, v_a, (1.0,2.0,2.0), (0.,-1.,-1.), (0.0,1.0), (0.,-1.), 1.414)

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
