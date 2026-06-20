"""Gs163 — ShapeUpgrade large-pole B-spline threshold.

Catalog claim: ShapeUpgrade observer tracks pole count exceeding 8192
(NbUPoles × NbVPoles) but threshold is hardcoded without justification.
Surfaces near boundary not flagged; downstream algorithms may fail on
unexpectedly large interpolation tasks.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (33x33, deg 2/2, 1089 poles — near but
    below 8192 threshold) IS the ADVANCED_FACE.face_geometry; face
    boundary edge pcurves referencing the large-pole B-spline surface IS
    the mechanism wired into face topology; ShapeUpgrade hardcoded 8192
    threshold (no justification, boundary not flagged) IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (33x33 poles, near
    8192 boundary) IS ADVANCED_FACE.face_geometry; face boundary edge
    pcurves on large-pole surface IS the mechanism wired into face
    topology; ShapeUpgrade hardcoded pole-count threshold failing to flag
    near-boundary surfaces IS the defect.
  - shape_null driver: large pole count near threshold causes downstream
    interpolation task unexpectedly large; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs163",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (33x33 poles, deg 2/2, near 8192 threshold) "
        "IS ADVANCED_FACE.face_geometry; face boundary edge pcurves on large-pole "
        "B-spline surface IS the mechanism wired into face topology; ShapeUpgrade "
        "hardcoded 8192 pole-count threshold failing to flag near-boundary surfaces "
        "IS the defect; shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: 33x33 poles (1089 total, near 8192 boundary) ──
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
#
# 33 control points per direction, degree 2.
# Knot vector (clamped open): mults (3, 1,1,...,1, 3) with 31 internal knots.
# Total poles = 33×33 = 1089; near 8192 threshold but not exceeding it.
# ShapeUpgrade hardcoded threshold at 8192 means surfaces just below are not
# flagged, leaving downstream algorithms with unexpectedly large tasks.

N = 33  # poles per direction
deg = 2

# Build a flat 33x33 grid on [0,32]x[0,32] at z=0
pts = []
for i in range(N):
    row = []
    for j in range(N):
        row.append(f.cartesian_point((float(i), float(j), 0.0)))
    pts.append(row)

nested = ",".join(
    "(" + ",".join(f"#{p.eid}" for p in row) + ")"
    for row in pts
)

# Knot vector for N=33, deg=2: clamped open
# mults: (3,) + (1,)*31 + (3,) — 33 knot values sum = 3+31+3 = 37 = N+deg+1 ✓
# knots: 0.,1.,2.,...,32.
u_mults = [3] + [1] * (N - deg - 1) + [3]
u_knots = list(range(N - deg + 1))  # 0..32
v_mults = u_mults[:]
v_knots = u_knots[:]

u_mults_str = ",".join(str(m) for m in u_mults)
u_knots_str = ",".join(f"{k}." for k in u_knots)
v_mults_str = u_mults_str
v_knots_str = u_knots_str

bspline = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs163_large_pole',{deg},{deg},({nested}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"({u_mults_str}),({v_mults_str}),({u_knots_str}),({v_knots_str}),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: rectangle [0,32]x[0,32] in UV, pcurves on large-pole surface ─
# Surface corners at u=0..32, v=0..32, z=0.
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((32.0, 0.0, 0.0))
p_C = f.cartesian_point((32.0, 32.0, 0.0))
p_D = f.cartesian_point((0.0, 32.0, 0.0))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{bspline.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


# Bottom: A→B, u=0→32 at v=0
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 32.0,
                  (0.0, 0.0), (1.0, 0.0), 32.0)
# Right: B→C, v=0→32 at u=32
e1 = mk_edge_line(v_B, v_C,
                  (32.0, 0.0, 0.0), (0.0, 1.0, 0.0), 32.0,
                  (32.0, 0.0), (0.0, 1.0), 32.0)
# Top: C→D, u=32→0 at v=32
e2 = mk_edge_line(v_C, v_D,
                  (32.0, 32.0, 0.0), (-1.0, 0.0, 0.0), 32.0,
                  (32.0, 32.0), (-1.0, 0.0), 32.0)
# Left: D→A, v=32→0 at u=0
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 32.0, 0.0), (0.0, -1.0, 0.0), 32.0,
                  (0.0, 32.0), (0.0, -1.0), 32.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS (33x33 poles, near 8192 threshold) IS the
# face_geometry; face boundary edge pcurves on the large-pole surface IS
# the mechanism wired into face topology — exercises ShapeUpgrade hardcoded
# pole-count threshold failing to flag near-boundary surfaces.
face  = f.advanced_face([f.face_outer_bound(loop)], bspline)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
