"""Gs121 — SurfaceNewton trapped in local minimum of distance function.

Catalog claim: ShapeAnalysis_Surface.SurfaceNewton can get trapped in a local
minimum when the surface has multiple local minima of the distance function.
Newton iteration doesn't escape the basin and returns a false minimum.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (degree=3, wavy control net with multiple
    humps creating multiple distance-function local minima) IS the
    ADVANCED_FACE.face_geometry; multi-hump surface geometry inducing Newton
    local-minimum trapping IS the mechanism wired into face topology;
    SurfaceNewton non-escaping iteration returning false minimum IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (degree=3, oscillating
    Z-values producing multiple humps with multiple local minima in the
    distance function) IS the ADVANCED_FACE.face_geometry; multi-minimum
    distance function IS the mechanism wired into face topology; SurfaceNewton
    local-minimum trapping without escape IS the defect.
  - shape_null driver: Newton false-minimum causes UV projection failure;
    strict kernels reject surface reference; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs121",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (degree=3, oscillating control net "
        "with multiple humps creating multiple distance-function local minima) "
        "IS ADVANCED_FACE.face_geometry; "
        "multi-minimum distance function IS the mechanism wired into face topology; "
        "SurfaceNewton non-escaping local-minimum trapping IS the defect; "
        "shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: degree=3, wavy multi-hump control net ────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# Cubic in both u and v; 6 poles in u and 2 in v.
# Z values alternate +1 / -1 in u direction → multiple humps.
# degree=3, 6 u-poles → sum_mults = 6+3+1 = 10; mults=(4,1,1,4) sum=10 ✓
# degree=1, 2 v-poles → mults=(2,2) sum=4 ✓
ctrl = [
    [(0.0, 0.0,  1.0), (0.2, 0.0, -1.0), (0.4, 0.0,  1.0),
     (0.6, 0.0, -1.0), (0.8, 0.0,  1.0), (1.0, 0.0, -1.0)],
    [(0.0, 1.0,  1.0), (0.2, 1.0, -1.0), (0.4, 1.0,  1.0),
     (0.6, 1.0, -1.0), (0.8, 1.0,  1.0), (1.0, 1.0, -1.0)],
]
ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(6)) + ")"
    for r in range(2)
) + ")"

bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs121_bss',3,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,1,1,4),(2,2),"
    f"(0.0,0.333,0.667,1.0),"
    f"(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square in parameter space ─────────────────────────────
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

e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), 1.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, -1.0), (0.0, 1.0, 0.0), 1.0,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 1.0, -1.0), (-1.0, 0.0, 0.0), 1.0,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 1.0, 1.0), (0.0, -1.0, 0.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS (multi-hump wavy net) IS the face_geometry;
# multiple Newton local minima IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
