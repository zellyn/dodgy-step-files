"""Gs094 — ShapeAnalysis_Surface.UVFromIso parameter-clamp underflow.

Catalog claim: Surface trimmed to subnormal parameter range u∈[1.0e-20, 1.0e-19].
UVFromIso's clamp logic doesn't handle subnormal/denormalized floats, causing
incorrect parameter mapping on extremely narrow domains.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (degree 1×1, bilinear) trimmed to subnormal
    U parameter range [1.0e-20, 1.0e-19] via PCURVE edges IS the
    ADVANCED_FACE.face_geometry; subnormal parameter range u∈[1e-20,1e-19] on
    face boundary IS the mechanism wired into face topology; UVFromIso clamp
    logic underflows on subnormal/denormalized floats, incorrect parameter
    mapping IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'),
                     contains(b'1e-20').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (bilinear, param domain
    u∈[0,1]) IS the ADVANCED_FACE.face_geometry; pcurve edges trimming the face
    to subnormal U range [1e-20, 1e-19] IS the mechanism wired into face topology;
    UVFromIso clamp underflows on subnormal floats, returns wrong UV IS the defect.
  - shape_null driver: incorrect UV mapping from subnormal clamp underflow;
    strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs094",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (bilinear) IS ADVANCED_FACE.face_geometry; "
        "pcurve edges trim face to subnormal U range [1e-20, 1e-19] IS the "
        "mechanism wired into face topology; UVFromIso clamp underflows on "
        "subnormal floats, incorrect parameter mapping IS the defect; shape_null"
    ),
)

# ── Bilinear B-spline over [0,1]×[0,1] ───────────────────────────────────────
ctrl = [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
    [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
]

ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]

cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(2)) + ")"
    for r in range(2)
) + ")"

# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs094_bss',1,1,"
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

# ── Face boundary: subnormal U strip u∈[1e-20, 1e-19], v∈[0,1] ───────────────
# Byte assertion: contains(b'1e-20')
# 3D corners (nearly coincident in X — subnormal range)
U_LO = 1e-20
U_HI = 1e-19

p_A = f.cartesian_point((U_LO, 0.0, 0.0))
p_B = f.cartesian_point((U_HI, 0.0, 0.0))
p_C = f.cartesian_point((U_HI, 1.0, 0.0))
p_D = f.cartesian_point((U_LO, 1.0, 0.0))

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

# e0: bottom A→B (v=0, u: 1e-20→1e-19) — subnormal U range
dU = U_HI - U_LO
e0 = mk_edge_line(v_A, v_B,
                  (U_LO, 0.0, 0.0), (1.0, 0.0, 0.0), dU,
                  (U_LO, 0.0), (1.0, 0.0), dU)
# e1: right B→C (u=1e-19, v: 0→1)
e1 = mk_edge_line(v_B, v_C,
                  (U_HI, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
                  (U_HI, 0.0), (0.0, 1.0), 1.0)
# e2: top C→D (v=1, u: 1e-19→1e-20)
e2 = mk_edge_line(v_C, v_D,
                  (U_HI, 1.0, 0.0), (-1.0, 0.0, 0.0), dU,
                  (U_HI, 1.0), (-1.0, 0.0), dU)
# e3: left D→A (u=1e-20, v: 1→0)
e3 = mk_edge_line(v_D, v_A,
                  (U_LO, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (U_LO, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry; subnormal U range [1e-20,1e-19] IS the mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
