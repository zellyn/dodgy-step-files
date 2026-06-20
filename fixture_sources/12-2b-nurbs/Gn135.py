"""Gn135 — B-spline curve non-uniform interior knots.

Catalog claim: Curve degree 2, 5 poles, interior knots at 0.4 and 0.45 create
an extremely narrow segment (width 0.05). ConvertCurveToBezier fails numerically
when extracting parameterization from this non-uniform, tightly-clustered knot
spacing.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 1 (V), 5×2 control net.
    U-direction encodes the catalog curve: 5 poles, interior knots at 0.4 and
    0.45 (narrow segment). IS the face surface (mechanism IS the face surface).
  - C-1 DRIVER: clustered interior knots 0.4/0.45 (span width 0.05) →
    ConvertCurveToBezier numerical instability in parameterization extraction.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 1 (V);
    5×2 control net; U knots (0.0, 0.4, 0.45, 1.0) mults (3,1,1,3) sum=8
    → n_u=5 ✓; V mults (2,2) knots (0.0,1.0); IS face surface;
    ConvertCurveToBezier clustered-knot numerical instability.
  - C-1 DRIVER: knot span 0.4..0.45 (width 0.05) → segment parameterization
    extraction fails.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn135",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 1 (V); "
        "5×2 control net; "
        "U knots (0.0,0.4,0.45,1.0) mults (3,1,1,3) — narrow segment span=0.05; "
        "V mults (2,2) knots (0.0,1.0); IS face surface; "
        "ConvertCurveToBezier clustered-knot numerical instability"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree-2 U × degree-1 V, 5×2 control net ──────
# U: n_u=5, p_u=2 → n_u+p_u+1=8. knots (0.0,0.4,0.45,1.0) mults (3,1,1,3) sum=8 ✓.
# V: n_v=2, p_v=1 → n_v+p_v+1=4. mults (2,2) sum=4 ✓. knots (0.0,1.0).
# Poles: spread across x=0..10 with two poles clustered near x=4 (the narrow segment).
u_row0 = [
    f.cartesian_point((0.0,  0.0, 0.0)),   # u=0
    f.cartesian_point((4.0,  1.0, 0.0)),   # before narrow segment at u=0.4
    f.cartesian_point((4.5,  1.2, 0.0)),   # narrow segment interior (u∈[0.4,0.45])
    f.cartesian_point((5.0,  1.0, 0.0)),   # after narrow segment at u=0.45
    f.cartesian_point((10.0, 0.0, 0.0)),   # u=1
]
u_row1 = [
    f.cartesian_point((0.0,  0.0, 1.0)),
    f.cartesian_point((4.0,  1.0, 1.0)),
    f.cartesian_point((4.5,  1.2, 1.0)),
    f.cartesian_point((5.0,  1.0, 1.0)),
    f.cartesian_point((10.0, 0.0, 1.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(u_row0)},{row_ids(u_row1)})"

mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn135_clustered_knots',2,1,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,1,1,3),(2,2),"
    f"(0.0,0.4,0.45,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# 3D corners: row0[0]=(0,0,0), row0[4]=(10,0,0), row1[4]=(10,0,1), row1[0]=(0,0,1).
p_a3 = f.cartesian_point((0.0,  0.0, 0.0))
p_b3 = f.cartesian_point((10.0, 0.0, 0.0))
p_c3 = f.cartesian_point((10.0, 0.0, 1.0))
p_d3 = f.cartesian_point((0.0,  0.0, 1.0))
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

# UV domain U∈[0,1] V∈[0,1]; 3D x=0..10, z=0..1.
e_bot   = mk_line_edge(vt_a, vt_b, (0.,0.,0.),  (1.,0.,0.),  (0.0,0.0), (1.,0.), 1.0)
e_right = mk_line_edge(vt_b, vt_c, (10.,0.,0.), (0.,0.,1.),  (1.0,0.0), (0.,1.), 1.0)
e_top   = mk_line_edge(vt_c, vt_d, (10.,0.,1.), (-1.,0.,0.), (1.0,1.0), (-1.,0.), 1.0)
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
