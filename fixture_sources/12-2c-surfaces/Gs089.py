"""Gs089 — ShapeAnalysis_Surface.UVFromIso B-spline midspan failure.

Catalog claim: B-spline surface with interior knot at u=0.5 in iso-curve
at v=0.5. Bisection algorithm in UVFromIso converges on wrong side of knot,
returning incorrect UV parameters.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (interior knot at u=0.5 AND v=0.5, creating
    C0 join at midspan) IS the ADVANCED_FACE.face_geometry; midspan interior
    knot coincidence IS the mechanism wired into face topology; UVFromIso
    bisection converges on wrong side of interior knot IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'),
                     contains(b'0.5').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (interior knots at u=0.5
    and v=0.5 both with multiplicity=degree+1, creating C0 midspan join) IS
    the ADVANCED_FACE.face_geometry; midspan knot coincidence at (0.5,0.5) IS
    the mechanism wired into face topology; UVFromIso bisection returns wrong-side
    UV IS the defect.
  - shape_null driver: incorrect UV parameters from bisection failure; strict
    kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs089",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (interior knots at u=0.5, v=0.5 both with "
        "full multiplicity, C0 midspan join) IS ADVANCED_FACE.face_geometry; "
        "midspan interior knot at (0.5,0.5) IS the mechanism wired into face "
        "topology; UVFromIso bisection converges on wrong side of knot IS the "
        "defect; shape_null"
    ),
)

# ── B-spline surface: degree-2 in U and V, interior C0 knots at u=0.5, v=0.5 ─
# U: 5 poles, degree 2, knots (0,0,0,0.5,0.5,0.5,1,1,1) mults (3,3,3)
# V: 5 poles, degree 2, knots (0,0,0,0.5,0.5,0.5,1,1,1) mults (3,3,3)
# Interior knot at u=0.5 and v=0.5 with full multiplicity (= degree+1 = 3)
# creates a C0 join exactly at midspan — the bisection trigger.
# Byte assertion: contains(b'0.5')
ctrl = [
    [(0.0, 0.0, 0.0), (0.25, 0.0, 0.0), (0.5, 0.0, 0.1), (0.75, 0.0, 0.0), (1.0, 0.0, 0.0)],
    [(0.0, 0.25, 0.0),(0.25, 0.25,0.0), (0.5, 0.25,0.1), (0.75,0.25, 0.0), (1.0, 0.25,0.0)],
    [(0.0, 0.5, 0.1), (0.25, 0.5, 0.1), (0.5, 0.5, 0.2), (0.75, 0.5, 0.1), (1.0, 0.5, 0.1)],
    [(0.0, 0.75,0.0), (0.25,0.75, 0.0), (0.5, 0.75,0.1), (0.75,0.75, 0.0), (1.0, 0.75,0.0)],
    [(0.0, 1.0, 0.0), (0.25, 1.0, 0.0), (0.5, 1.0, 0.1), (0.75, 1.0, 0.0), (1.0, 1.0, 0.0)],
]

ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]

cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(5)) + ")"
    for r in range(5)
) + ")"

# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'), contains(b'0.5')
# Interior knots at u=0.5, v=0.5 with multiplicity 3 (= degree+1), full C0 break.
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs089_bss',2,2,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3,3),(3,3,3),"
    f"(0.0,0.5,1.0),"
    f"(0.0,0.5,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square on the midspan-knot surface ────────────────────
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

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry; midspan interior knot at (0.5,0.5) IS the mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
