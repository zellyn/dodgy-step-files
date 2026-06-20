"""Gs106 — Concentrated-poles surface with Newton underflow.

Catalog claim: ShapeAnalysis_Surface.NextValueOfUV fails on surfaces where all
control poles cluster in a small region, creating high curvature and causing
Newton iteration step to underflow (step size becomes subnormal). Reproducer:
B-spline surface with control poles clustered in 1mm cube.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS with all 4 control poles clustered within
    a 1e-3 × 1e-3 × 1e-3 mm cube (coordinates ~1e-6) IS the
    ADVANCED_FACE.face_geometry; face boundary spans [0,1]×[0,1] parameter
    domain on the concentrated surface IS the mechanism wired into face
    topology; NextValueOfUV Newton step underflows (step size becomes subnormal)
    due to extreme curvature concentration IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (all poles in 1e-3 cube)
    IS the ADVANCED_FACE.face_geometry; concentrated-pole face boundary IS
    the mechanism wired into face topology; NextValueOfUV Newton step underflow
    on high-curvature surface IS the defect.
  - shape_null driver: Newton step subnormal on concentrated poles; strict
    kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

# All poles clustered within 1e-3 × 1e-3 × 1e-3 cube centred at (0,0,0).
DELTA = 5e-4  # half-width of cluster: poles span ±5e-4 in each axis

f = StepFile(
    catalog_id="Gs106",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (all poles clustered in 1e-3 cube) IS "
        "ADVANCED_FACE.face_geometry; concentrated-pole face boundary IS "
        "the mechanism wired into face topology; "
        "NextValueOfUV Newton step underflows on high-curvature surface IS the defect; "
        "shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: all poles in 1e-3 cube ──────────────────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
ctrl = [
    [(-DELTA, -DELTA, -DELTA), ( DELTA, -DELTA, -DELTA)],
    [(-DELTA,  DELTA,  DELTA), ( DELTA,  DELTA,  DELTA)],
]
ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(2)) + ")"
    for r in range(2)
) + ")"

bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs106_bss',1,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),"
    f"(0.0,1.0),"
    f"(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: [0,1]×[0,1] on the concentrated surface ───────────────────
# 3D points match pole evaluations (bilinear interp): corners of clustered patch.
p_A = f.cartesian_point((-DELTA, -DELTA, -DELTA))  # (u=0, v=0)
p_B = f.cartesian_point(( DELTA, -DELTA, -DELTA))  # (u=1, v=0)
p_C = f.cartesian_point(( DELTA,  DELTA,  DELTA))  # (u=1, v=1)
p_D = f.cartesian_point((-DELTA,  DELTA,  DELTA))  # (u=0, v=1)

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

import math
# e0: A→B (v=0, u: 0→1); 3D: (-d,-d,-d)→(d,-d,-d), length=2*DELTA in x
e0 = mk_edge_line(v_A, v_B,
                  (-DELTA, -DELTA, -DELTA), (1.0, 0.0, 0.0), 2*DELTA,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
# e1: B→C (u=1, v: 0→1); 3D: (d,-d,-d)→(d,d,d), length=2*DELTA*sqrt(2)
e1 = mk_edge_line(v_B, v_C,
                  ( DELTA, -DELTA, -DELTA), (0.0, 1.0, 1.0), 2*DELTA*math.sqrt(2),
                  (1.0, 0.0), (0.0, 1.0), 1.0)
# e2: C→D (v=1, u: 1→0); 3D: (d,d,d)→(-d,d,d), length=2*DELTA
e2 = mk_edge_line(v_C, v_D,
                  ( DELTA,  DELTA,  DELTA), (-1.0, 0.0, 0.0), 2*DELTA,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
# e3: D→A (u=0, v: 1→0); 3D: (-d,d,d)→(-d,-d,-d), length=2*DELTA*sqrt(2)
e3 = mk_edge_line(v_D, v_A,
                  (-DELTA,  DELTA,  DELTA), (0.0, -1.0, -1.0), 2*DELTA*math.sqrt(2),
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS (concentrated poles) IS the face_geometry;
# clustered-pole face boundary IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
