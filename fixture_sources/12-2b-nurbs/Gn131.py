"""Gn131 — ShapeFix_ComposeShell.SplitOnEdges B-spline pcurve tangent-mismatch.

Catalog claim: B-spline surface with a closed edge whose 3D curve is C1-smooth
but whose 2D pcurve has a C0 knot at u=0.5. ShapeFix_ComposeShell.SplitOnEdges
detects the C0 discontinuity in the pcurve and proposes a split at that knot.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree 2 (U) × 2 (V), 4×4 control net.
    IS the face surface (mechanism IS the face surface).
  - One EDGE_CURVE uses a B_SPLINE_CURVE_WITH_KNOTS as its 3D curve (C1
    smooth across the full domain) and a B_SPLINE_CURVE_WITH_KNOTS as its
    pcurve (on the surface) that has a full-multiplicity interior knot at
    u=0.5, making it C0 there.
  - C-1 DRIVER: pcurve C0 knot at interior parameter → SplitOnEdges proposes
    split → kernel heal/reject triggered.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V);
    4×4 control net; IS face surface; defect EDGE_CURVE 3D curve is
    B_SPLINE_CURVE_WITH_KNOTS degree=2, C1-smooth; pcurve is
    B_SPLINE_CURVE_WITH_KNOTS degree=2 with interior knot mult=3 (full) at
    u=0.5 → C0 discontinuity in pcurve tangent.
  - C-1 DRIVER: pcurve C0 knot (mult=degree+1 at interior) → tangent jump.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn131",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V); "
        "4×4 control net; IS face surface; "
        "defect EDGE_CURVE 3D curve B_SPLINE_CURVE_WITH_KNOTS degree=2 C1-smooth; "
        "pcurve B_SPLINE_CURVE_WITH_KNOTS degree=2 interior knot mult=3 at u=0.5 → C0 tangent-mismatch; "
        "SplitOnEdges proposes split → kernel heal/reject"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree-2 U × degree-2 V, 4×4 control net ──────
# U: n_u=4, p_u=2 → n_u+p_u+1=7. mults (3,1,3) → sum=7 ✓. knots (0.0,0.5,1.0).
# V: n_v=4, p_v=2 → n_v+p_v+1=7. mults (3,1,3) → sum=7 ✓. knots (0.0,0.5,1.0).
# Control net rows (V outer, U inner):
r0 = [f.cartesian_point((float(u), 0.0, 0.0)) for u in range(4)]
r1 = [f.cartesian_point((float(u), 1.0, 0.5)) for u in range(4)]
r2 = [f.cartesian_point((float(u), 2.0, 0.5)) for u in range(4)]
r3 = [f.cartesian_point((float(u), 3.0, 0.0)) for u in range(4)]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)},{row_ids(r3)})"

mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn131_surf',2,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,1,3),(3,1,3),"
    f"(0.0,0.5,1.0),(0.0,0.5,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── 3D B-spline curve for the defect edge (C1, degree 2, 5 poles) ─────────────
# Runs along U-direction at V=0 (z=0 row of surface): U from 0→3, V=0.
# degree 2, 5 poles → n+p+1=8. mults (3,2,3) → sum=8 ✓. knots (0,0.5,1).
c3d_poles = [
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.cartesian_point((0.75, 0.0, 0.0)),
    f.cartesian_point((1.5, 0.0, 0.0)),
    f.cartesian_point((2.25, 0.0, 0.0)),
    f.cartesian_point((3.0, 0.0, 0.0)),
]
c3d_ids = "(" + ",".join(f"#{p.eid}" for p in c3d_poles) + ")"
curve_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn131_c3d',2,{c3d_ids},"
    f".UNSPECIFIED.,.F.,.F.,(3,2,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# ── Pcurve: C0 at u=0.5 (degree 2, mult=3 interior) ──────────────────────────
# degree 2, 5 poles → n+p+1=8. mults (3,3,3) → sum=9 ≠ 8.
# Use 6 poles: n+p+1=9. mults (3,3,3) → sum=9 ✓.
# Full multiplicity at interior knot 0.5 → C0 (tangent jump).
pc2d_poles = [
    f.cartesian_point((0.0, 0.0)),
    f.cartesian_point((0.6, 0.0)),
    f.cartesian_point((1.2, 0.0)),   # segment 1 end
    f.cartesian_point((1.8, 0.0)),   # segment 2 start (C0 join)
    f.cartesian_point((2.4, 0.0)),
    f.cartesian_point((3.0, 0.0)),
]
pc2d_ids = "(" + ",".join(f"#{p.eid}" for p in pc2d_poles) + ")"
pc2d_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn131_pc2d',2,{pc2d_ids},"
    f".UNSPECIFIED.,.F.,.F.,(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

pcd = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pcdef',(#{pc2d_curve.eid}),#{prc.eid})"
)
pc = f._emit_raw(f"PCURVE('pc',#{mech_surf.eid},#{pcd.eid})")
sc = f._emit_raw(f"SURFACE_CURVE('sc',#{curve_3d.eid},(#{pc.eid}),.PCURVE_S1.)")

# ── Remaining boundary edges (simple lines) ────────────────────────────────────
# Corners: A=(0,0,0) B=(3,0,0) C=(3,3,0) D=(0,3,0)
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((3.0, 0.0, 0.0))
p_c3 = f.cartesian_point((3.0, 3.0, 0.0))
p_d3 = f.cartesian_point((0.0, 3.0, 0.0))
vt_a = f.vertex_point(p_a3)
vt_b = f.vertex_point(p_b3)
vt_c = f.vertex_point(p_c3)
vt_d = f.vertex_point(p_d3)

# Defect edge: A→B using the b-spline surface_curve above.
e_bot = f._emit_raw(
    f"EDGE_CURVE('ec_bot',#{vt_a.eid},#{vt_b.eid},#{sc.eid},.T.)"
)

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

# UV domain [0,1]×[0,1] maps to 3D [0,3]×[0,3]×0.
e_right = mk_line_edge(vt_b, vt_c, (3.,0.,0.), (0.,1.,0.), (1.0,0.0), (0.,1.), 1.0)
e_top   = mk_line_edge(vt_c, vt_d, (3.,3.,0.), (-1.,0.,0.),(1.0,1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(vt_d, vt_a, (0.,3.,0.), (0.,-1.,0.),(0.0,1.0), (0.,-1.), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], mech_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
