"""Gn129 — Geom_BSplineSurface periodic-U-closure weight-extraction.

Catalog claim: Geom_BSplineSurface periodic-U-closure weight-extraction.
B-spline surface with U-periodic knot vector (period 2π), 4×3 poles, rational
(one weight in wrapped pole row = 0.8). IUPeriodic() + ShapeAnalysis_Surface
weight extraction at wrap seam exposes the off-unity weight unexpectedly.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree 3 (U) × 2 (V), 4×3 control net,
    rational with one weight in the pole net = 0.8 (all others = 1.0).
    U knot vector spans [0, 2π] with mults suggesting periodicity.
    When IUPeriodic() is called and the surface is re-queried for weights at
    the seam, the wrapped row exposes the 0.8 weight where 1.0 is expected.
    IS the face surface (mechanism IS the face surface).
  - C-1 DRIVER: U-periodic wrap + off-unity seam weight → weight extraction
    mismatch → kernel heal/reject triggered.

Mechanism vs driver:
  - CATALOG MECHANISM: RATIONAL_B_SPLINE_SURFACE + B_SPLINE_SURFACE_WITH_KNOTS
    degree=3 (U) × 2 (V); 4×3 control net; weights all=1.0 except pole[0][2]=0.8;
    U mults (4,1,1,4) knots (0.0,2.094,4.189,6.283) (near 2π-periodic);
    V mults (3,3) knots (0.0,1.0); IS face surface;
    IUPeriodic seam weight mismatch → kernel heal/reject.
  - C-1 DRIVER: off-unity weight at U-periodic seam → weight extraction failure.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn129",
    defect=(
        "RATIONAL_B_SPLINE_SURFACE + B_SPLINE_SURFACE_WITH_KNOTS degree=3 (U) × 2 (V); "
        "4×3 control net; weight[0][2]=0.8 (others=1.0); "
        "U mults (4,1,1,4) knots (0.0,2.094,4.189,6.283) (near 2π-periodic); "
        "V mults (3,3) knots (0.0,1.0); IS face surface; "
        "IUPeriodic seam weight 0.8 mismatch → kernel heal/reject"
    ),
)

# ── CATALOG MECHANISM SURFACE: rational B-spline, periodic-U, off-unity weight ─
# degree U=3, V=2.  Control net 4 (U-cols) × 3 (V-rows).
# U: n_u=4, p_u=3 → n_u+p_u+1=8. mults (4,1,1,4) → sum=10... need sum=8.
# Use mults (3,1,1,3) → sum=8 ✓. knots (0.0, 2.094, 4.189, 6.283).
# V: n_v=3, p_v=2 → n_v+p_v+1=6. mults (3,3) → sum=6 ✓. knots (0.0, 1.0).
# Weights: 4×3 = 12 weights. pole[0][2] (v-row 0, u-col 2) = 0.8, rest = 1.0.
# Control net: 4 u-columns × 3 v-rows.
# Row v=0 (z=0): u=0→3 columns
v0 = [
    f.cartesian_point((0.0,  1.0, 0.0)),   # u=0
    f.cartesian_point((1.0,  1.0, 0.0)),   # u=1
    f.cartesian_point((2.0,  1.0, 0.0)),   # u=2  ← weight=0.8
    f.cartesian_point((3.0,  1.0, 0.0)),   # u=3
]
# Row v=1 (z=1)
v1 = [
    f.cartesian_point((0.0,  0.0, 1.0)),
    f.cartesian_point((1.0,  0.5, 1.0)),
    f.cartesian_point((2.0,  0.5, 1.0)),
    f.cartesian_point((3.0,  0.0, 1.0)),
]
# Row v=2 (z=2)
v2 = [
    f.cartesian_point((0.0, -1.0, 2.0)),
    f.cartesian_point((1.0, -0.5, 2.0)),
    f.cartesian_point((2.0, -0.5, 2.0)),
    f.cartesian_point((3.0, -1.0, 2.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

# STEP net: outer list = V-rows, inner = U-cols.
cp_net = f"({row_ids(v0)},{row_ids(v1)},{row_ids(v2)})"

# Weights: 3 rows × 4 cols. pole[0][2] = 0.8 (v-row 0, u-col 2).
# STEP weight order matches cp_net (row-major, V outer, U inner).
w_row0 = "(1.0,1.0,0.8,1.0)"
w_row1 = "(1.0,1.0,1.0,1.0)"
w_row2 = "(1.0,1.0,1.0,1.0)"
weights = f"({w_row0},{w_row1},{w_row2})"

# Emit as complex entity: RATIONAL_B_SPLINE_SURFACE + B_SPLINE_SURFACE_WITH_KNOTS.
# degree U=3, V=2; mults U=(3,1,1,3) sum=8 ✓; mults V=(3,3) sum=6 ✓.
mech_surf = f._emit_raw(
    f"(RATIONAL_B_SPLINE_SURFACE({weights})"
    f"B_SPLINE_SURFACE('gn129_periodic_u_weight',3,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.)"
    f"B_SPLINE_SURFACE_WITH_KNOTS((3,1,1,3),(3,3),"
    f"(0.0,2.094,4.189,6.283),(0.0,1.0),.UNSPECIFIED.)"
    f"GEOMETRIC_REPRESENTATION_ITEM()"
    f"REPRESENTATION_ITEM('gn129_surf'))"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# UV domain: U ∈ [0, 6.283], V ∈ [0, 1].
# 3D boundary corners: v0[0]=(0,1,0), v0[3]=(3,1,0), v2[0]=(0,-1,2), v2[3]=(3,-1,2).
p_a3 = f.cartesian_point((0.0,  1.0, 0.0))
p_b3 = f.cartesian_point((3.0,  1.0, 0.0))
p_c3 = f.cartesian_point((3.0, -1.0, 2.0))
p_d3 = f.cartesian_point((0.0, -1.0, 2.0))
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

# V=0 bottom (U: 0→6.283), U=6.283 right (V: 0→1),
# V=1 top (U: 6.283→0), U=0 left (V: 1→0).
e_bot   = mk_line_edge(vt_a, vt_b, (0.,1.,0.),  (1.,0.,0.), (0.0,0.0), (1.,0.), 3.0)
e_right = mk_line_edge(vt_b, vt_c, (3.,1.,0.),  (0.,-1.,1.),(6.283,0.0),(0.,1.), 1.0)
e_top   = mk_line_edge(vt_c, vt_d, (3.,-1.,2.), (-1.,0.,0.),(6.283,1.0),(-1.,0.), 3.0)
e_left  = mk_line_edge(vt_d, vt_a, (0.,-1.,2.), (0.,1.,-1.),(0.0,1.0),  (0.,-1.), 1.0)

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
