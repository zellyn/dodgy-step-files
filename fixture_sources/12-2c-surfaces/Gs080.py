"""Gs080 — ShapeUpgrade_FaceDivide.SplitSurface boundary-merge.

Catalog claim: B_SPLINE_SURFACE with internal knot at natural face boundary.
SplitSurface splits at boundary-coincident knot, producing degenerate sub-face
with coincident control points.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (internal knot at u=1.0 coinciding with face
    boundary) IS the ADVANCED_FACE.face_geometry; knot-at-boundary coincidence
    IS the mechanism wired into face topology; SplitSurface splits at boundary
    knot producing degenerate zero-area sub-face IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'),
                     contains(b'gs080').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (knot multiplicity=3 at u=1.0
    exactly on face boundary) IS the ADVANCED_FACE.face_geometry; boundary-coincident
    internal knot IS the mechanism wired into face topology; SplitSurface produces
    degenerate sub-face with coincident poles IS the defect.
  - shape_null driver: degenerate zero-area patch; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs080",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (knot at u=1.0 coincides with face boundary) "
        "IS ADVANCED_FACE.face_geometry; boundary-coincident internal knot IS the "
        "mechanism wired into face topology; SplitSurface produces degenerate "
        "sub-face with coincident poles IS the defect; shape_null"
    ),
)

# ── B-spline surface: degree-2 in U, degree-1 in V ───────────────────────────
# U knots: (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0)  → multiplicity (3,3,3)
# This places an internal knot at u=1.0 with full multiplicity (= degree+1 = 3),
# creating a C0 join — the knot lands exactly on the face boundary (u_max=1.0).
# The face covers u∈[0,1]: SplitSurface splits here, producing a degenerate patch.
# V: degree 1, 2 control points → knots (0.0,0.0,1.0,1.0), mults (2,2)
ctrl = [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)],   # u=0
    [(0.5, 0.0, 0.0), (0.5, 1.0, 0.0)],   # u=0.5
    [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],   # u=1.0 — boundary-coincident knot
    [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],   # u=1.0 — coincident poles (degenerate split)
    [(1.5, 0.0, 0.0), (1.5, 1.0, 0.0)],   # u=1.5
    [(2.0, 0.0, 0.0), (2.0, 1.0, 0.0)],   # u=2.0
]

ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]

cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(2)) + ")"
    for r in range(6)
) + ")"

# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'), contains(b'gs080')
# u_knots: (0.0, 1.0, 2.0) with mults (3,3,3) → knot-at-boundary coincidence
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs080_bss',2,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3,3),(2,2),"
    f"(0.0,1.0,2.0),"
    f"(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square in U∈[0,1], V∈[0,1] ───────────────────────────
# Face boundary coincides with the internal knot at u=1.0.
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
# e1: right B→C (u=1, v: 0→1) — boundary at boundary-coincident knot
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

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry; boundary-coincident knot IS the mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
