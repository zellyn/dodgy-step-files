"""Gs010 — Self-intersecting / folded B_SPLINE_SURFACE_WITH_KNOTS
(Jacobian sign change, transposed interior rows).

Catalog claim: A B_SPLINE_SURFACE_WITH_KNOTS whose interior control rows are
transposed so that the parametric mapping folds back on itself; Jacobian sign
flips within the parameter domain (non-injective surface). Kernels that silently
use this surface for projection or intersection produce wrong results.

OCC behavior: silently accepts (no diagnostic, empty result).
Expected: occt=empty. Closure intent: ambiguous (heal or reject).

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree 3×2, 4×3 control net, clamped knots
    U(4,4) V(3,3); interior rows swapped so surface folds.
    Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS('),
                     contains(b'(15.0,5.0,2.0)'),
                     contains(b'(0.0,5.0,2.0)').
  - Tier-3 assertion: shape_null == True.
  - Four SURFACE_CURVE/PCURVE edges wire the folded surface into face topology.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS with transposed interior
    rows IS the ADVANCED_FACE.face_geometry; Jacobian sign change makes the
    surface non-injective; shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs010",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree 3x2 4x3 net clamped (4,4)x(3,3) "
        "knots; interior rows transposed (row1 beyond row2 in X) → Jacobian "
        "sign change; non-injective folded surface; contains (15.0,5.0,2.0) "
        "and (0.0,5.0,2.0); IS ADVANCED_FACE.face_geometry; shape_null=True"
    ),
)

# ── CATALOG MECHANISM: folded BSpline surface, degree 3×2, 4×3 control net ───
# Normal layout would be X increasing with U: row0 at X=0, row1 at X=5,
#   row2 at X=10, row3 at X=15.
# TRANSPOSED: row1 and row2 are swapped so row1 is at X=15 and row2 is at X=5.
# This causes the surface to fold back: u parameter increases but X goes 0→15→5→15,
# making the Jacobian (dS/du) flip sign in the middle.
#
# Byte assertions:
#   (15.0,5.0,2.0)  appears in row1 col2 (index [1][2])
#   (0.0,5.0,2.0)   appears in row0 col2 (index [0][2])
#
# 4 rows × 3 cols; degree 3 in U, degree 2 in V.
# U knots: (0.0, 1.0) mults (4,4) → sum = 8 = 3+4+1 ✓
# V knots: (0.0, 1.0) mults (3,3) → sum = 6 = 2+3+1 ✓

def cp(x, y, z):
    return f.cartesian_point((x, y, z))

# row0 at X=0 (normal first row)
r0 = [cp(0.0,  0.0, 0.0), cp(0.0, 5.0, 0.0), cp(0.0, 5.0, 2.0)]
# row1 at X=15 (transposed: should be X=5 but swapped with row2)
r1 = [cp(15.0, 0.0, 0.0), cp(15.0, 5.0, 0.0), cp(15.0, 5.0, 2.0)]
# row2 at X=5 (transposed: should be X=10 but swapped/wrong order)
r2 = [cp(5.0,  0.0, 0.0), cp(5.0,  5.0, 0.0), cp(5.0,  5.0, 2.0)]
# row3 at X=15 again (same as row1 creates fold)
r3 = [cp(15.0, 0.0, 0.0), cp(15.0, 5.0, 0.0), cp(15.0, 5.0, 2.0)]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)},{row_ids(r3)})"

surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs010_folded',3,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,4),(3,3),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Four line edges wiring the folded surface into the face loop ───────────────
# Use UV corner approximations for 3D positions:
# (u=0, v=0) → row0[0] = (0,0,0)
# (u=1, v=0) → row3[0] = (15,0,0)
# (u=1, v=1) → row3[2] = (15,5,2) — but use (15,5,0) for wire simplicity
# (u=0, v=1) → row0[2] = (0,5,2)  — but use (0,5,0) for wire simplicity
p_a = f.cartesian_point((0.0,  0.0, 0.0))
p_b = f.cartesian_point((15.0, 0.0, 0.0))
p_c = f.cartesian_point((15.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0,  5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

def mk_line_edge(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

# Bottom: v_a→v_b (u: 0→1, v=0)
e0 = mk_line_edge(v_a, v_b,
    (0.0,  0.0, 0.0), (1.0, 0.0, 0.0), 15.0,
    (0.0, 0.0),       (1.0, 0.0),        1.0)
# Right: v_b→v_c (v: 0→1, u=1)
e1 = mk_line_edge(v_b, v_c,
    (15.0, 0.0, 0.0), (0.0, 1.0, 0.0), 5.0,
    (1.0, 0.0),       (0.0, 1.0),       1.0)
# Top: v_c→v_d (u: 1→0, v=1)
e2 = mk_line_edge(v_c, v_d,
    (15.0, 5.0, 0.0), (-1.0, 0.0, 0.0), 15.0,
    (1.0, 1.0),        (-1.0, 0.0),       1.0)
# Left: v_d→v_a (v: 1→0, u=0)
e3 = mk_line_edge(v_d, v_a,
    (0.0, 5.0, 0.0), (0.0, -1.0, 0.0), 5.0,
    (0.0, 1.0),      (0.0, -1.0),       1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# Folded B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
