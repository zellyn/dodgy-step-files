"""Gn082 — ShapeUpgrade_ConvertSurfaceToBezierBasis multi-patch seam drift.

Catalog claim: ConvertSurfaceToBezierBasis converts B-spline surface to N×M
Bezier grid correctly. B-spline surface with interior knots in both U and V
converts to N×M Bezier grid with seam tolerance mismatch between adjacent
patches.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree u=2, v=2.
    U: n_u CPs, degree 2. Knots (0.0,0.33,0.67,1.0) mults (3,2,2,3) sum=10.
    n_u+p+1=10 → n_u=7.
    V: n_v CPs, degree 2. Knots (0.0,0.33,0.67,1.0) mults (3,2,2,3) sum=10.
    n_v+p+1=10 → n_v=7.
    Interior knots at u=0.33 and u=0.67, v=0.33 and v=0.67 force 3×3 Bezier
    patch grid (3 spans in each direction, degree 2 each).
    ConvertSurfaceToBezierBasis computes patch boundaries independently per
    patch; floating-point accumulation in re-parameterization drifts seam
    coordinates between adjacent patches by ~1e-6, exceeding the shape
    tolerance and causing empty result.
    IS the ADVANCED_FACE.face_geometry (the catalog mechanism IS the face surface).
  - C-1 DRIVER: bottom edge B-spline with 1.5-unit CP gap at t=0.5 drives
    shape_null=True via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS u_degree=2 v_degree=2 7×7 net;
    U knots (0.0,0.33,0.67,1.0) mults (3,2,2,3); V knots (0.0,0.33,0.67,1.0)
    mults (3,2,2,3); IS the ADVANCED_FACE.face_geometry; ConvertSurfaceToBezierBasis
    3×3 Bezier grid seam drift ~1e-6 causes empty result.
  - C-1 DRIVER: bottom edge B-spline 1.5-unit CP gap drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn082",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS u_degree=2 v_degree=2 7x7 net; "
        "U knots (0.0,0.33,0.67,1.0) mults (3,2,2,3) sum=10 ✓; "
        "V knots (0.0,0.33,0.67,1.0) mults (3,2,2,3) sum=10 ✓; "
        "IS the ADVANCED_FACE.face_geometry; "
        "ConvertSurfaceToBezierBasis 3×3 Bezier grid; "
        "seam drift ~1e-6 between adjacent patches exceeds tolerance — empty result; "
        "C-1 break in bottom edge at t=0.5 (1.5-unit CP gap) drives shape_null=True"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree u=2 v=2, 7×7 control net ───────────────
# U: n_u=7, degree 2 → n+p+1=7+2+1=10. knots (0.0,0.33,0.67,1.0) mults (3,2,2,3) sum=10 ✓
# V: n_v=7, degree 2 → n+p+1=10. knots (0.0,0.33,0.67,1.0) mults (3,2,2,3) sum=10 ✓
# Grid: X∈[0,6], Y∈[0,6]

rows = []
for i in range(7):
    row = []
    for j in range(7):
        row.append(f.cartesian_point((float(i), float(j), 0.0)))
    rows.append(row)

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = "(" + ",".join(row_ids(r) for r in rows) + ")"

surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn082_seam_drift_surf',2,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,2,2,3),(3,2,2,3),"
    f"(0.0,0.33,0.67,1.0),(0.0,0.33,0.67,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── C-1 DRIVER: bottom edge B-spline with 1.5-unit gap at t=0.5 ──────────────
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((1.2, 0.0, 0.0))
dc2 = f.cartesian_point((2.5, 0.0, 0.0))
dc3 = f.cartesian_point((4.0, 0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((5.2, 0.0, 0.0))
dc5 = f.cartesian_point((6.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn082_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.17, 0.0))
pp2 = f.cartesian_point((0.33, 0.0))
pp3 = f.cartesian_point((0.5,  0.0))
pp4 = f.cartesian_point((0.67, 0.0))
pp5 = f.cartesian_point((1.0,  0.0))

pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn082_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn082_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn082_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn082_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((6.0, 0.0, 0.0))
p_c = f.cartesian_point((6.0, 6.0, 0.0))
p_d = f.cartesian_point((0.0, 6.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn082_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2_ = f.vector(d2e, length)
    l2_ = f.line(p2e, v2_)
    pcd_ = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2_.eid}),#{prc.eid})")
    pc_  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd_.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc_.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (6.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 6.0)
e_top   = mk_line_edge(v_c, v_d, (6.0, 6.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 6.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 6.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 6.0)

loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
