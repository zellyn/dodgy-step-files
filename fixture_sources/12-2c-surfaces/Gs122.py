"""Gs122 — Rational B-spline surface with zero weight (degenerate interior).

Catalog claim: ShapeUpgrade_SplitSurface processes a rational B-spline surface
where one interior weight is 0, producing a degenerate interior region. The
split operation doesn't validate weight coherence post-split.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - RATIONAL_B_SPLINE_SURFACE (with one interior weight = 0.0, all others
    positive) combined with B_SPLINE_SURFACE_WITH_KNOTS IS the
    ADVANCED_FACE.face_geometry; zero interior weight causing degenerate
    homogeneous coordinate at one control point IS the mechanism wired into
    face topology; SplitSurface weight coherence check absence IS the defect.
  - Byte assertions: contains(b'RATIONAL_B_SPLINE_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: RATIONAL_B_SPLINE_SURFACE (weight[1][1] = 0.0 among
    3x3 control points) IS the ADVANCED_FACE.face_geometry; zero interior
    weight producing degenerate homogeneous coordinate IS the mechanism wired
    into face topology; SplitSurface post-split weight coherence absence
    IS the defect.
  - shape_null driver: zero-weight interior control point renders surface
    undefined at that region; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs122",
    defect=(
        "RATIONAL_B_SPLINE_SURFACE (weight[1][1]=0.0 among 3x3 control points, "
        "all others positive) IS ADVANCED_FACE.face_geometry; "
        "zero interior weight producing degenerate homogeneous coordinate "
        "IS the mechanism wired into face topology; "
        "SplitSurface post-split weight coherence check absence IS the defect; "
        "shape_null"
    ),
)

# ── RATIONAL_B_SPLINE_SURFACE with zero interior weight ───────────────────────
# Byte assertion: contains(b'RATIONAL_B_SPLINE_SURFACE')
# Uses STEP complex entity combining B_SPLINE_SURFACE_WITH_KNOTS and
# RATIONAL_B_SPLINE_SURFACE (weights listed separately in rational form).
# degree=1 in both u and v; 3×3 pole grid.
# mults=(2,1,2) sum=5 → n_poles = 5-1-1 = 3 ✓ for degree=1.
# weight[1][1] = 0.0 (center pole) → degenerate interior.
ctrl = [
    [(0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (1.0, 0.0, 0.0)],
    [(0.0, 0.5, 0.0), (0.5, 0.5, 0.0), (1.0, 0.5, 0.0)],
    [(0.0, 1.0, 0.0), (0.5, 1.0, 0.0), (1.0, 1.0, 0.0)],
]
ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(3)) + ")"
    for r in range(3)
) + ")"

# Weights: all 1.0 except center (row=1, col=1) = 0.0.
weights_str = "((1.0,1.0,1.0),(1.0,0.0,1.0),(1.0,1.0,1.0))"

# Complex entity: B_SPLINE_SURFACE_WITH_KNOTS + RATIONAL_B_SPLINE_SURFACE.
bss = f._emit_raw(
    f"(B_SPLINE_SURFACE('gs122_bss',1,1,{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.)"
    f"B_SPLINE_SURFACE_WITH_KNOTS((2,1,2),(2,1,2),"
    f"(0.0,0.5,1.0),(0.0,0.5,1.0),.UNSPECIFIED.)"
    f"GEOMETRIC_REPRESENTATION_ITEM()"
    f"RATIONAL_B_SPLINE_SURFACE({weights_str})"
    f"REPRESENTATION_ITEM('gs122_rbss')"
    f"SURFACE())"
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
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 1.0, 0.0), (-1.0, 0.0, 0.0), 1.0,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RATIONAL_B_SPLINE_SURFACE (zero interior weight) IS the face_geometry;
# degenerate homogeneous coordinate IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
