"""Gn143 — RectangularTrimmedSurface Basis Unwrap Null-Check.

Catalog claim: A RECTANGULAR_TRIMMED_SURFACE wrapping a B-spline basis surface.
When the healer unwraps the basis for Bezier conversion, it may receive a null
pointer if the basis surface lacks the expected type tag. The null-check on the
unwrapped basis pointer is missing, causing a crash or incorrect result when the
basis surface is a B_SPLINE_SURFACE_WITH_KNOTS.

STEP mechanism (literal):
  - RECTANGULAR_TRIMMED_SURFACE wrapping a B_SPLINE_SURFACE_WITH_KNOTS
    degree=2 (U) × 2 (V), 4×4 control net.
    The trimmed surface IS the face surface; the B-spline is the basis.
  - C-1 DRIVER: RectangularTrimmedSurface basis pointer unwrap → missing
    null-check on dynamic cast of basis to BSplineSurface → null deref or
    incorrect dispatch when basis type is unexpected.

Mechanism vs driver:
  - CATALOG MECHANISM: RECTANGULAR_TRIMMED_SURFACE with
    trim range U1=0.2, U2=0.8, V1=0.2, V2=0.8 (sub-range of [0,1]²);
    basis = B_SPLINE_SURFACE_WITH_KNOTS degree=2 × 2, 4×4 control net;
    U knots (0.0,0.5,1.0) mults (3,1,3) sum=7 → n_u=4 ✓;
    V knots (0.0,0.5,1.0) mults (3,1,3) sum=7 → n_v=4 ✓;
    RECTANGULAR_TRIMMED_SURFACE IS the face surface;
    basis unwrap null-check missing → null deref / wrong dispatch.
  - C-1 DRIVER: dynamic cast of RectangularTrimmedSurface.BasisSurface to
    BSplineSurface returns unexpected type → unchecked null pointer.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn143",
    defect=(
        "RECTANGULAR_TRIMMED_SURFACE (U1=0.2,U2=0.8,V1=0.2,V2=0.8) wrapping "
        "B_SPLINE_SURFACE_WITH_KNOTS degree=2 × 2; 4×4 control net; "
        "U/V knots (0.0,0.5,1.0) mults (3,1,3) → n_u=n_v=4; "
        "RECTANGULAR_TRIMMED_SURFACE IS face surface; "
        "basis unwrap missing null-check → null deref / wrong dispatch on BSplineSurface cast"
    ),
)

# ── Basis B-spline surface: degree-2 U × degree-2 V, 4×4 control net ─────────
# U: n_u=4, p_u=2 → n_u+p_u+1=7. knots (0.0,0.5,1.0) mults (3,1,3) sum=7 ✓.
# V: n_v=4, p_v=2 → n_v+p_v+1=7. knots (0.0,0.5,1.0) mults (3,1,3) sum=7 ✓.
# Control net: 4 V-rows × 4 U-cols; surface spans x=0..9, y=0..9.
r0 = [f.cartesian_point((0.,0.,0.)), f.cartesian_point((3.,0.5,0.)),
      f.cartesian_point((6.,0.5,0.)), f.cartesian_point((9.,0.,0.))]
r1 = [f.cartesian_point((0.,3.,0.5)), f.cartesian_point((3.,3.,1.)),
      f.cartesian_point((6.,3.,1.)),  f.cartesian_point((9.,3.,0.5))]
r2 = [f.cartesian_point((0.,6.,0.5)), f.cartesian_point((3.,6.,1.)),
      f.cartesian_point((6.,6.,1.)),  f.cartesian_point((9.,6.,0.5))]
r3 = [f.cartesian_point((0.,9.,0.)), f.cartesian_point((3.,9.,0.5)),
      f.cartesian_point((6.,9.,0.5)), f.cartesian_point((9.,9.,0.))]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)},{row_ids(r3)})"

basis_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn143_basis',2,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,1,3),(3,1,3),"
    f"(0.0,0.5,1.0),(0.0,0.5,1.0),"
    f".UNSPECIFIED.)"
)

# ── RectangularTrimmedSurface wrapping the basis ───────────────────────────────
# Trim range U1=0.2, U2=0.8, V1=0.2, V2=0.8 within basis domain [0,1]².
# usense=.T. vsense=.T.
mech_surf = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('gn143_rts',#{basis_surf.eid},"
    f"0.2,0.8,0.2,0.8,.T.,.T.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# The face lives in the trimmed parameter domain U∈[0.2,0.8], V∈[0.2,0.8].
# We evaluate approximate 3D corners by blending the control net:
# At u=0.2, v=0.2 the surface is near r0[0]→r1[0] blend; approximate (1.8,1.8,0).
# Use simple approximations consistent with a smooth quad surface.
p_a3 = f.cartesian_point((1.8, 1.8, 0.3))
p_b3 = f.cartesian_point((7.2, 1.8, 0.3))
p_c3 = f.cartesian_point((7.2, 7.2, 0.3))
p_d3 = f.cartesian_point((1.8, 7.2, 0.3))
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

# Pcurve parametric domain matches the trimmed surface: U∈[0.2,0.8], V∈[0.2,0.8].
# Use parametric length 0.6 in each direction.
e_bot   = mk_line_edge(vt_a, vt_b, (1.8,1.8,0.3), (1.,0.,0.),  (0.2,0.2), (1.,0.),  0.6)
e_right = mk_line_edge(vt_b, vt_c, (7.2,1.8,0.3), (0.,1.,0.),  (0.8,0.2), (0.,1.),  0.6)
e_top   = mk_line_edge(vt_c, vt_d, (7.2,7.2,0.3), (-1.,0.,0.), (0.8,0.8), (-1.,0.), 0.6)
e_left  = mk_line_edge(vt_d, vt_a, (1.8,7.2,0.3), (0.,-1.,0.), (0.2,0.8), (0.,-1.), 0.6)

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
