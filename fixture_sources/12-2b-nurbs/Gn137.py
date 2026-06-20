"""Gn137 — B-spline curve precision asymmetry in split.

Catalog claim: Curve with 7 poles, degree 3. The split logic uses an asymmetric
tolerance test (parU - param < prec) instead of Abs(parU - param) < prec. If a
split parameter exceeds a knot by epsilon, the loop exits prematurely, skipping
valid patches in the Bezier decomposition.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree=3 (U) × 1 (V), 7×2 control net.
    Interior knots at 0.333 and 0.667, plus a split candidate slightly above
    0.333 (encoded via knot placement). IS the face surface (mechanism IS the
    face surface).
  - C-1 DRIVER: asymmetric tolerance (parU - param < prec not |...| < prec) →
    split parameter ε above knot → loop exits early → patch segments skipped.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=3 (U) × 1 (V);
    7×2 control net; U knots (0.0, 0.333, 0.667, 1.0) mults (4,1,1,4)
    → n_u+p_u+1=11, n_u=7 ✓; V mults (2,2) knots (0.0,1.0); IS face surface;
    asymmetric split tolerance → patch skip.
  - C-1 DRIVER: one-directional tolerance on split loop → premature exit when
    split param > knot by epsilon.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn137",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=3 (U) × 1 (V); "
        "7×2 control net; "
        "U knots (0.0,0.333,0.667,1.0) mults (4,1,1,4); "
        "V mults (2,2) knots (0.0,1.0); IS face surface; "
        "asymmetric split tolerance (parU-param<prec not |...|<prec) → patch segments skipped"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree-3 U × degree-1 V, 7×2 control net ──────
# U: n_u=7, p_u=3 → n_u+p_u+1=11. mults (4,1,1,1,4) sum=11 → need 5 distinct knots:
#   knots (0.0, 0.333, 0.5, 0.667, 1.0) mults (4,1,1,1,4) sum=11 ✓.
#   Three interior knots model three Bezier segments with two where
#   split asymmetry triggers the bug.
# V: n_v=2, p_v=1 → n_v+p_v+1=4. mults (2,2) sum=4 ✓. knots (0.0,1.0).
u_row0 = [
    f.cartesian_point((0.0,  0.0, 0.0)),
    f.cartesian_point((1.0,  1.5, 0.0)),
    f.cartesian_point((2.0,  2.0, 0.0)),   # near first interior knot 0.333
    f.cartesian_point((3.5,  1.8, 0.0)),   # straddles 0.5 knot
    f.cartesian_point((5.0,  1.5, 0.0)),   # near second interior knot 0.667
    f.cartesian_point((6.5,  0.8, 0.0)),
    f.cartesian_point((7.0,  0.0, 0.0)),
]
u_row1 = [
    f.cartesian_point((0.0,  0.0, 1.0)),
    f.cartesian_point((1.0,  1.5, 1.0)),
    f.cartesian_point((2.0,  2.0, 1.0)),
    f.cartesian_point((3.5,  1.8, 1.0)),
    f.cartesian_point((5.0,  1.5, 1.0)),
    f.cartesian_point((6.5,  0.8, 1.0)),
    f.cartesian_point((7.0,  0.0, 1.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(u_row0)},{row_ids(u_row1)})"

mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn137_prec_asymm',3,1,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,1,1,1,4),(2,2),"
    f"(0.0,0.333,0.5,0.667,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# 3D corners: row0[0]=(0,0,0), row0[6]=(7,0,0), row1[6]=(7,0,1), row1[0]=(0,0,1).
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((7.0, 0.0, 0.0))
p_c3 = f.cartesian_point((7.0, 0.0, 1.0))
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

# UV domain U∈[0,1] V∈[0,1]; 3D x=0..7, z=0..1.
e_bot   = mk_line_edge(vt_a, vt_b, (0.,0.,0.),  (1.,0.,0.),  (0.0,0.0), (1.,0.), 1.0)
e_right = mk_line_edge(vt_b, vt_c, (7.,0.,0.),  (0.,0.,1.),  (1.0,0.0), (0.,1.), 1.0)
e_top   = mk_line_edge(vt_c, vt_d, (7.,0.,1.),  (-1.,0.,0.), (1.0,1.0), (-1.,0.), 1.0)
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
