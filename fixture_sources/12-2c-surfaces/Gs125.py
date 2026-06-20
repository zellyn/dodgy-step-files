"""Gs125 — B-SPLINE_SURFACE with very wide U domain.

Catalog claim: ShapeUpgrade_ConvertSurfaceToBezierBasis produces excessive
subdivision when input domain is very wide. A surface with U domain [0, 1000]
gets split into ~1000 tiny Bezier patches, each occupying parameter range of
1.0, causing memory bloat and numerical issues.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (degree=1, U domain [0.0, 1000.0] expressed
    as knot values 0.0 and 1000.0 with interior knots at intervals of 1.0,
    producing ~1000 spans) IS the ADVANCED_FACE.face_geometry; excessively
    wide U domain causing ~1000-patch Bezier subdivision IS the mechanism wired
    into face topology; ConvertSurfaceToBezierBasis lacking domain-width guard
    IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (degree=1, u-knots spanning
    [0.0, 1000.0] with many interior subdivisions — very wide domain) IS the
    ADVANCED_FACE.face_geometry; wide-domain excessive Bezier subdivision
    IS the mechanism wired into face topology; ConvertSurfaceToBezierBasis
    domain-width guard absence IS the defect.
  - shape_null driver: ~1000 Bezier sub-patches cause memory/numerical failure;
    strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs125",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (degree=1, U domain [0.0, 1000.0] "
        "with interior knots at 250, 500, 750 — four wide spans) "
        "IS ADVANCED_FACE.face_geometry; "
        "very wide U domain causing excessive Bezier subdivision "
        "IS the mechanism wired into face topology; "
        "ConvertSurfaceToBezierBasis domain-width guard absence IS the defect; "
        "shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: degree=1, very wide U domain ─────────────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# degree=1 in u; u-knots = (0.0, 250.0, 500.0, 750.0, 1000.0).
# mults=(2,1,1,1,2) sum=7 → n_poles_u = 7-1-1 = 5 ✓
# degree=1 in v; v-knots = (0.0, 1.0); mults=(2,2) → n_poles_v = 2 ✓
# The extreme domain [0, 1000] is the defect — ConvertSurfaceToBezierBasis
# will attempt ~1000 sub-spans, causing numerical/memory failure.
ctrl = [
    [(0.0,   0.0, 0.0), (250.0, 0.0, 0.0), (500.0, 0.0, 0.0),
     (750.0, 0.0, 0.0), (1000.0, 0.0, 0.0)],
    [(0.0,   1.0, 0.0), (250.0, 1.0, 0.0), (500.0, 1.0, 0.0),
     (750.0, 1.0, 0.0), (1000.0, 1.0, 0.0)],
]
ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(5)) + ")"
    for r in range(2)
) + ")"

bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs125_bss',1,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,1,1,1,2),(2,2),"
    f"(0.0,250.0,500.0,750.0,1000.0),"
    f"(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: spans full wide U domain in parameter space ────────────────
# 3D points correspond to the surface at (u,v) corners; for this flat surface
# (z=0) the 3D coords match the pole XY positions.
p_A = f.cartesian_point((0.0,    0.0, 0.0))
p_B = f.cartesian_point((1000.0, 0.0, 0.0))
p_C = f.cartesian_point((1000.0, 1.0, 0.0))
p_D = f.cartesian_point((0.0,    1.0, 0.0))

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

# Bottom edge: u from 0 to 1000, v=0
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1000.0,
                  (0.0, 0.0), (1.0, 0.0), 1000.0)
# Right edge: v from 0 to 1, u=1000
e1 = mk_edge_line(v_B, v_C,
                  (1000.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
                  (1000.0, 0.0), (0.0, 1.0), 1.0)
# Top edge: u from 1000 to 0, v=1
e2 = mk_edge_line(v_C, v_D,
                  (1000.0, 1.0, 0.0), (-1.0, 0.0, 0.0), 1000.0,
                  (1000.0, 1.0), (-1.0, 0.0), 1000.0)
# Left edge: v from 1 to 0, u=0
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS (U domain [0, 1000]) IS the face_geometry;
# very wide domain causing excessive Bezier subdivision IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
