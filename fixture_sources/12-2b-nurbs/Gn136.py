"""Gn136 — NURBS iterator loop boundary fault in split.

Catalog claim: Surface with 4×3 control grid, degree 2/1. The Build method's
iterator variables j1/j2 never reset between outer loop iterations over U splits,
causing patches to be skipped when split parameters are non-monotonic relative to
knot ordering.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 1 (V), 4×3 control net.
    Two interior U-knots (0.333, 0.667) create three Bezier patches.
    IS the face surface (mechanism IS the face surface).
  - C-1 DRIVER: two interior U-knots → three Bezier patches; iterator j1/j2
    not reset between patches → second/third patch skipped in Build.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 1 (V);
    4×3 control net; U knots (0.0, 0.333, 0.667, 1.0) mults (3,1,1,3)
    → n_u+p_u+1=8 → need n_u=5; extend to 5 U-poles; V mults (3,3) knots
    (0.0,1.0); IS face surface; Build iterator j1/j2 not reset → patches skipped.
  - C-1 DRIVER: 3-patch decomposition with non-reset iterator → loop exits early.

Note: catalog says 4×3 grid; to match degree=2, U mults (3,1,1,3) sum=8 requires
n_u=5 (not 4). We use 5×3 to satisfy the knot constraint while preserving the
4-segment spirit (3 interior spans visible in the patch structure).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn136",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 1 (V); "
        "5×3 control net (extended from catalog 4×3 to satisfy knot sum); "
        "U knots (0.0,0.333,0.667,1.0) mults (3,1,1,3); V mults (3,3) knots (0.0,1.0); "
        "IS face surface; Build iterator j1/j2 not reset between U-patch loop → patches skipped"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree-2 U × degree-1 V, 5×3 control net ──────
# U: n_u=5, p_u=2 → n_u+p_u+1=8. mults (3,1,1,3) sum=8 ✓. knots (0,0.333,0.667,1).
# V: n_v=3, p_v=1 → n_v+p_v+1=5. mults (2,1,2) sum=5 ✓. knots (0.0,0.5,1.0).
# Control net: 3 V-rows × 5 U-cols.
r0 = [f.cartesian_point((float(u), 0.0, 0.0)) for u in range(5)]
r1 = [f.cartesian_point((float(u), 1.0, 0.5)) for u in range(5)]
r2 = [f.cartesian_point((float(u), 2.0, 0.0)) for u in range(5)]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)})"

mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn136_iter_fault',2,1,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,1,1,3),(2,1,2),"
    f"(0.0,0.333,0.667,1.0),(0.0,0.5,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# 3D corners: r0[0]=(0,0,0), r0[4]=(4,0,0), r2[4]=(4,2,0), r2[0]=(0,2,0).
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((4.0, 0.0, 0.0))
p_c3 = f.cartesian_point((4.0, 2.0, 0.0))
p_d3 = f.cartesian_point((0.0, 2.0, 0.0))
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

# UV domain U∈[0,1] V∈[0,1]; 3D x=0..4, y=0..2.
e_bot   = mk_line_edge(vt_a, vt_b, (0.,0.,0.),  (1.,0.,0.),  (0.0,0.0), (1.,0.), 1.0)
e_right = mk_line_edge(vt_b, vt_c, (4.,0.,0.),  (0.,1.,0.),  (1.0,0.0), (0.,1.), 1.0)
e_top   = mk_line_edge(vt_c, vt_d, (4.,2.,0.),  (-1.,0.,0.), (1.0,1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(vt_d, vt_a, (0.,2.,0.),  (0.,-1.,0.), (0.0,1.0), (0.,-1.), 1.0)

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
