"""Gn025 — Folded/non-injective BSpline surface (Jacobian flip).

Catalog claim: A B_SPLINE_SURFACE_WITH_KNOTS whose control net has interior
rows that swap order, producing a fold where the Jacobian flips sign within
the parameter range; surface is non-injective.

OCC behavior: silently accepts the folded surface and uses it for projection
without a diagnostic. Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree (3,1), 5 rows x 2 columns.
    Row spacing deliberately has rows 2 and 3 (0-indexed) transposed in Y:
      Row 0: Y=0.0  (bottom)
      Row 1: Y=2.0
      Row 2: Y=4.0  — would be monotone
      Row 3: Y=3.0  — SWAPPED BACK (Y drops from 4.0 → 3.0): fold!
      Row 4: Y=6.0  (top)
    This causes the Jacobian (∂S/∂u) to flip sign between rows 2 and 3.
    V knots (0,1) mults (2,2) sum=4=1+2+1 ✓ (degree 1, 2 cols).
    U knots (0,1) mults (4,4) sum=8=3+4+1 ✓ (degree 3, 5 rows? No: 4+4=8=3+5+1=9? No).
    For degree p=3 and n+1=5 rows: knot sum = n+1+p+1 = 5+3+1 = 9.
    Use (0, 0.5, 1) mults (4, 1, 4) sum = 9 = 5+3+1 ✓.
  - C-1 DRIVER: bottom edge B_SPLINE_CURVE_WITH_KNOTS degree-2 positional break
    at t=0.5 (CP[2]=(3.0,0,0) vs CP[3]=(4.5,0,0), 1.5-unit gap) forces shape_null.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS 5x2 net with rows 2/3 transposed
    (Y: 0, 2, 4, 3, 6) — Jacobian sign flip producing a non-injective folded surface.
  - C-1 DRIVER: B-spline positional break at t=0.5 forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn025",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree (3,1) 5x2 net; "
        "U knots (0.0,0.5,1.0) mults (4,1,4) sum=9=3+5+1 ✓; "
        "V knots (0.0,1.0) mults (2,2) sum=4=1+2+1 ✓; "
        "rows Y=(0.0,2.0,4.0,3.0,6.0) — rows 2/3 transposed causing Jacobian flip; "
        "non-injective folded surface: ∂S/∂u changes sign between rows 2 and 3; "
        "defect edge B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(3.0,0,0) vs CP[3]=(4.5,0,0), 1.5-unit gap) drives shape_null=True"
    ),
)

# ── DEFECT SURFACE: B_SPLINE_SURFACE_WITH_KNOTS with folded rows ─────────────
# 5 rows in U (degree 3), 2 columns in V (degree 1).
# X spans [0,6] (column 0: X=0, column 1: X=6).
# Y values per row: 0, 2, 4, 3 (FOLD!), 6 → non-monotone → Jacobian flip.
y_vals = [0.0, 2.0, 4.0, 3.0, 6.0]  # row 3 swapped back: fold between rows 2 and 3

rows = []
for y in y_vals:
    col0 = f.cartesian_point((0.0, y, 0.0))
    col1 = f.cartesian_point((6.0, y, 0.0))
    rows.append((col0, col1))

cp_rows = ",".join(
    f"(#{r[0].eid},#{r[1].eid})"
    for r in rows
)

# U: degree 3, 5 rows → knot sum = 5+3+1=9; use (0, 0.5, 1) mults (4,1,4) = 9 ✓
# V: degree 1, 2 cols → knot sum = 2+1+1=4; use (0, 1) mults (2,2) = 4 ✓
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('folded_surface',3,1,"
    f"({cp_rows}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,1,4),(2,2),"
    f"(0.0,0.5,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

# ── Parametric context ────────────────────────────────────────────────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners (surface U∈[0,1], V∈[0,1]; 3D corners at rows 0/4, cols 0/1)
p_a = f.cartesian_point((0.0, 0.0, 0.0))   # U=0, V=0
p_b = f.cartesian_point((6.0, 0.0, 0.0))   # U=0, V=1
p_c = f.cartesian_point((6.0, 6.0, 0.0))   # U=1, V=1
p_d = f.cartesian_point((0.0, 6.0, 0.0))   # U=1, V=0
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)


def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, len3)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, len3)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


e_right = mk_edge_with_pc(v_b, v_c, (6.0, 0.0, 0.0), (0., 1., 0.), 6.0, (1.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (6.0, 6.0, 0.0), (-1., 0., 0.), 6.0, (1.0, 1.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 6.0, 0.0), (0., -1., 0.), 6.0, (0.0, 1.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) — C-1 DRIVER ───────────────────────────
# degree-2 B-spline with 1.5-unit positional gap at t=0.5 forces shape_null.
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((1.5, 0.0, 0.0))
dc2 = f.cartesian_point((3.0, 0.0, 0.0))   # end of first Bezier
dc3 = f.cartesian_point((4.5, 0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((5.5, 0.0, 0.0))
dc5 = f.cartesian_point((6.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('folded_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.25, 0.0))
pp2 = f.cartesian_point((0.5,  0.0))
pp3 = f.cartesian_point((0.5,  0.0))
pp4 = f.cartesian_point((0.75, 0.0))
pp5 = f.cartesian_point((1.0,  0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('folded_c1_break_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('folded_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('folded_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('folded_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('folded_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
