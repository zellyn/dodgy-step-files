"""Gs070 — ShapeUpgrade_SplitSurfaceContinuity trimmed-fallback skips C0 knot.

Catalog claim: A B-spline surface with a C0 knot at parameter 0.5 in U (double
interior knot, degree 3, so multiplicity 3 = degree = C0 discontinuity). Wrapped in
a RECTANGULAR_TRIMMED_SURFACE. SplitSurfaceContinuity.Compute() should subdivide at
the C0 knot, but the trim-aware fallback path skips the subdivision, leaving the
tangent-discontinuity edge unhandled.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - RECTANGULAR_TRIMMED_SURFACE (wrapping B_SPLINE_SURFACE_WITH_KNOTS with C0 knot
    at u=0.5) IS the ADVANCED_FACE.face_geometry; C0 interior knot (multiplicity=3,
    degree=3) IS the mechanism wired into face topology; trim-fallback skips
    subdivision IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'),
                     contains(b'RECTANGULAR_TRIMMED_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: RECTANGULAR_TRIMMED_SURFACE IS the ADVANCED_FACE.face_geometry;
    B-spline C0 interior knot at u=0.5 (multiplicity=3=degree) IS the mechanism wired
    into face topology; SplitSurfaceContinuity trim-fallback skips subdivision IS the defect.
  - shape_null driver: C0 discontinuity not split; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs070",
    defect=(
        "RECTANGULAR_TRIMMED_SURFACE (wrapping B_SPLINE_SURFACE_WITH_KNOTS with C0 "
        "knot at u=0.5) IS ADVANCED_FACE.face_geometry; C0 interior knot multiplicity=3 "
        "IS the mechanism wired into face topology; SplitSurfaceContinuity trim-fallback "
        "skips subdivision IS the defect; shape_null"
    ),
)

# ── B-spline surface: degree 3 in U, degree 1 in V ───────────────────────────
# U knots: (4, 3, 4) → knot vector [0,0,0,0, 0.5,0.5,0.5, 1,1,1,1]
# Multiplicity 3 at u=0.5 with degree=3 → C0 (tangent) discontinuity.
# Control points: 7 cols (u), 2 rows (v); jump in Y at col 3 (the C0 break).
ctrl_pts = []
for row_idx, y_base in enumerate([0.0, 1.0]):
    row = []
    ys = [0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0]  # C0 jump at col 3
    for col_idx in range(7):
        x = col_idx / 6.0
        y = y_base
        z = ys[col_idx]  # Z encodes the C0 discontinuity at u=0.5
        row.append(f.cartesian_point((x, y, z)))
    ctrl_pts.append(row)

# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(7)) + ")"
    for r in range(2)
) + ")"

bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs070_bss',3,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,3,4),(2,2),(0.0,0.5,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

# ── RECTANGULAR_TRIMMED_SURFACE: trim to u∈[0.1, 0.9], v∈[0, 1] ─────────────
# Trim domain straddles the C0 knot at u=0.5, forcing Compute to deal with it.
# Byte assertion: contains(b'RECTANGULAR_TRIMMED_SURFACE')
trimmed = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('gs070_trim',#{bss.eid},"
    "0.1,0.9,0.0,1.0,.T.,.T.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the trimmed surface ──────────────────────────────
# 3D corners: u=0.1 → x≈0.017, u=0.9 → x≈0.150; v=0/1 → y=0/1; z from spline
# Approximate 3D from control points near corners
p_A = f.cartesian_point((0.1, 0.0, 0.0))
p_B = f.cartesian_point((0.9, 0.0, 1.0))
p_C = f.cartesian_point((0.9, 1.0, 1.0))
p_D = f.cartesian_point((0.1, 1.0, 0.0))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{trimmed.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# e0: bottom A→B (v=0, u: 0.1→0.9)
e0 = mk_edge_line(v_A, v_B,
                  (0.1, 0.0, 0.0), (0.8, 0.0, 1.0), 0.8,
                  (0.1, 0.0), (1.0, 0.0), 0.8)
# e1: right B→C (u=0.9, v: 0→1)
e1 = mk_edge_line(v_B, v_C,
                  (0.9, 0.0, 1.0), (0.0, 1.0, 0.0), 1.0,
                  (0.9, 0.0), (0.0, 1.0), 1.0)
# e2: top C→D (v=1, u: 0.9→0.1)
e2 = mk_edge_line(v_C, v_D,
                  (0.9, 1.0, 1.0), (-0.8, 0.0, -1.0), 0.8,
                  (0.9, 1.0), (-1.0, 0.0), 0.8)
# e3: left D→A (u=0.1, v: 1→0)
e3 = mk_edge_line(v_D, v_A,
                  (0.1, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (0.1, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RECTANGULAR_TRIMMED_SURFACE IS the face_geometry; C0 knot IS the mechanism on face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], trimmed)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
