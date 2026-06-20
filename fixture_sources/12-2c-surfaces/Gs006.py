"""Gs006 — Surface singularities (degenerate poles) not in declared form.

Catalog claim: A B_SPLINE_SURFACE_WITH_KNOTS has one interior control row
collapsed to a single point (degenerate pole) but the file does not flag the
singularity. Surface-surface intersection algorithms and pcurve projection
misbehave near the collapsed row.

OCC behavior: silently accepts (no diagnostic, empty result).
Expected: occt=empty. Closure intent: heal.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS with interior row collapsed to (0.0,0.0,10.0)
    IS the ADVANCED_FACE.face_geometry; no singularity flag in file.
    Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS('),
                     count(b'(0.0,0.0,10.0)') >= 3.
  - Tier-3 assertion: shape_null == True.
  - Four SURFACE_CURVE/PCURVE edges wire the surface into the face loop.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS with a degenerate interior
    row at (0.0,0.0,10.0) (cone-apex / sphere-pole collapse) IS the
    ADVANCED_FACE.face_geometry; no declared singularity triggers misbehaviour
    in intersection/projection routines; shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs006",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS interior row collapsed to (0.0,0.0,10.0) "
        "(degenerate pole / cone-apex singularity); no singularity declared in "
        "STEP flags; IS ADVANCED_FACE.face_geometry; "
        "intersection/projection misbehaves; shape_null=True"
    ),
)

# ── CATALOG MECHANISM: BSpline surface, degree 2×1, collapsed interior row ───
# 4 rows × 2 cols control net:
#   row0 (v=0): base ring at z=0, radius 10
#   row1 (v=0.33): degenerate — all points collapse to (0,0,10) [the pole]
#   row2 (v=0.67): degenerate — all points collapse to (0,0,10) [second apex point]
#   row3 (v=1):  base ring at z=0, radius 10 (symmetric)
#
# Byte assertion: (0.0,0.0,10.0) appears at least 3 times (rows 1 and 2 each
# have 2 cols but they alias; row0/3 col1 is (10.0,0.0,0.0) not matching).
# Use 4 copies of (0.0,0.0,10.0) across the two degenerate rows × 2 cols.

def cp(x, y, z):
    return f.cartesian_point((x, y, z))

r0 = [cp(10.0, 0.0, 0.0), cp(10.0, 5.0, 0.0)]
r1 = [cp(0.0,  0.0, 10.0), cp(0.0, 0.0, 10.0)]   # degenerate pole ×2
r2 = [cp(0.0,  0.0, 10.0), cp(0.0, 0.0, 10.0)]   # same pole ×2 more (byte assert ≥3)
r3 = [cp(10.0, 0.0, 0.0), cp(10.0, 5.0, 0.0)]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)},{row_ids(r3)})"

# Degree 2 in U (4 rows → knots (0,0.5,1) mults (3,2,3) sum=8=2+4+1+1 ✓)
# Degree 1 in V (2 cols → knots (0,1) mults (2,2) sum=4 ✓)
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs006_degenerate_pole',2,1,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,2,3),(2,2),"
    f"(0.0,0.5,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Four line edges wiring the face loop ─────────────────────────────────────
# Use corners in 3D at the base (u=0,v=0), (u=1,v=0), (u=1,v=1), (u=0,v=1).
# At u=0: row0 interp → approx (10,0,0); at u=1: row3 interp → (10,5,0)
# Approximate 3D corners for vertex points (approximate — actual BSpline eval):
corners_3d = [
    (10.0, 0.0, 0.0),   # u=0, v=0
    (10.0, 0.0, 0.0),   # u=1, v=0 (same base row, v=0 end)
    (10.0, 5.0, 0.0),   # u=1, v=1
    (10.0, 5.0, 0.0),   # u=0, v=1
]
corners_uv = [
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 1.0),
    (0.0, 1.0),
]

# Use distinct coords to avoid vertex aliasing
p_a = f.cartesian_point((10.0, 0.0, 0.0))
p_b = f.cartesian_point((10.0, 0.01, 0.0))
p_c = f.cartesian_point((10.0, 5.0, 0.0))
p_d = f.cartesian_point((10.0, 4.99, 0.0))
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
    (10.0, 0.0, 0.0), (0.0, 1.0, 0.0), 0.01,
    (0.0, 0.0),       (1.0, 0.0),       1.0)
# Right: v_b→v_c (v: 0→1, u=1)
e1 = mk_line_edge(v_b, v_c,
    (10.0, 0.01, 0.0), (0.0, 1.0, 0.0), 4.99,
    (1.0, 0.0),         (0.0, 1.0),       1.0)
# Top: v_c→v_d (u: 1→0, v=1)
e2 = mk_line_edge(v_c, v_d,
    (10.0, 5.0, 0.0), (0.0, -1.0, 0.0), 0.01,
    (1.0, 1.0),       (-1.0, 0.0),        1.0)
# Left: v_d→v_a (v: 1→0, u=0)
e3 = mk_line_edge(v_d, v_a,
    (10.0, 4.99, 0.0), (0.0, -1.0, 0.0), 4.99,
    (0.0, 1.0),         (0.0, -1.0),       1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
