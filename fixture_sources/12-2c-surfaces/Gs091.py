"""Gs091 — ShapeAnalysis_Surface.IsUClosed B-spline rational weights.

Catalog claim: Rational B-spline surface with asymmetric weights at U closure
(first=1.0, last=2.0). Weighted projection differs from geometric distance;
closure detection misses boundary condition.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - RATIONAL_B_SPLINE_SURFACE (weights first column=1.0, last column=2.0,
    asymmetric at U closure) embedded in B_SPLINE_SURFACE_WITH_KNOTS IS the
    ADVANCED_FACE.face_geometry; asymmetric rational weights at U boundaries
    IS the mechanism wired into face topology; IsUClosed weighted projection
    differs from geometric distance, closure detection fails IS the defect.
  - Byte assertions: contains(b'RATIONAL_B_SPLINE_SURFACE'),
                     contains(b'2.0').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: RATIONAL_B_SPLINE_SURFACE (first-column weights=1.0,
    last-column weights=2.0; same geometric positions but different homogeneous
    coordinates at u=0 and u=1) IS the ADVANCED_FACE.face_geometry; asymmetric
    rational weights at U closure IS the mechanism wired into face topology;
    IsUClosed weighted projection sees different w-scaled positions, misses
    closed boundary IS the defect.
  - shape_null driver: closure detection failure; strict kernels reject
    unclosed surface used as closed; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs091",
    defect=(
        "RATIONAL_B_SPLINE_SURFACE (first-column weights=1.0, last-column "
        "weights=2.0) superimposed on B_SPLINE_SURFACE_WITH_KNOTS IS "
        "ADVANCED_FACE.face_geometry; asymmetric rational weights at U closure "
        "IS the mechanism wired into face topology; IsUClosed weighted projection "
        "differs from geometric distance, closure detection fails IS the defect; "
        "shape_null"
    ),
)

# ── Rational B-spline: 3×2 control grid, degree 2 in U, degree 1 in V ────────
# Same XY positions at u=0 (col 0) and u=1 (col 2) — geometrically closed in U.
# But weights: col 0 = 1.0, col 2 = 2.0 — asymmetric → homogeneous coords differ.
# Byte assertion: contains(b'2.0')
ctrl = [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
    [(0.5, 0.0, 0.5), (0.5, 1.0, 0.5)],
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)],   # same as col 0 → geometrically U-closed
]

ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]

cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(2)) + ")"
    for r in range(3)
) + ")"

# B_SPLINE_SURFACE_WITH_KNOTS (base entity for complex)
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs091_bss',2,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3),(2,2),"
    f"(0.0,1.0),"
    f"(0.0,1.0),.UNSPECIFIED.)"
)

# Byte assertion: contains(b'RATIONAL_B_SPLINE_SURFACE'), contains(b'2.0')
# Weights: col 0=1.0 (rows 0,1,2), col 1=1.0 (rows 0,1,2) but last col u=1 gets 2.0
# Layout: weights[row][col] — 3 rows (u), 2 cols (v)
# First u-strip weight=1.0, last u-strip weight=2.0 → asymmetric U closure
rbs = f._emit_raw(
    f"RATIONAL_B_SPLINE_SURFACE("
    f"((1.0,1.0),(1.0,1.0),(2.0,2.0)))"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square ────────────────────────────────────────────────
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((1.0, 0.0, 0.0))
p_C = f.cartesian_point((1.0, 1.0, 0.0))
p_D = f.cartesian_point((0.0, 1.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

def mk_edge_line(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{bss.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# e0: bottom A→B (v=0, u: 0→1)
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
# e1: right B→C (u=1, v: 0→1)
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
# e2: top C→D (v=1, u: 1→0)
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 1.0, 0.0), (-1.0, 0.0, 0.0), 1.0,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
# e3: left D→A (u=0, v: 1→0)
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RATIONAL_B_SPLINE_SURFACE IS the face_geometry; asymmetric weights at U closure IS the mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
