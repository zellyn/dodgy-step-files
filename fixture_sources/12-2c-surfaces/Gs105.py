"""Gs105 — FaceDivide crossing-curves defect.

Catalog claim: ShapeUpgrade_FaceDivide.SplitCurves fails when splitting curves
cross each other. The algorithm doesn't handle intersection between splitter
curves and produces overlapping sub-faces on same surface.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (unit square) IS the ADVANCED_FACE.face_geometry;
    face boundary loop contains two EDGE_CURVEs whose pcurves cross each other
    at (u=0.5, v=0.5), with winding that creates a self-intersecting boundary
    IS the mechanism wired into face topology; FaceDivide.SplitCurves fails
    on the crossing intersection and produces overlapping sub-faces IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (unit square) IS the
    ADVANCED_FACE.face_geometry; self-intersecting pcurve boundary with
    crossing at (0.5,0.5) IS the mechanism wired into face topology;
    FaceDivide.SplitCurves does not handle crossing splitters IS the defect.
  - shape_null driver: self-intersecting face boundary produces overlapping
    sub-faces; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs105",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (unit square) IS ADVANCED_FACE.face_geometry; "
        "self-intersecting pcurve boundary with crossing at (0.5,0.5) IS "
        "the mechanism wired into face topology; "
        "FaceDivide.SplitCurves does not handle crossing splitters IS the defect; "
        "shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: unit square ──────────────────────────────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
ctrl = [
    [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)],
    [(0.0, 1.0, 0.0), (1.0, 1.0, 0.0)],
]
ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(2)) + ")"
    for r in range(2)
) + ")"

bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs105_bss',1,1,"
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

# ── Self-intersecting face boundary: two diagonal edges crossing at (0.5,0.5) ─
# Vertices at corners (A,B,C,D) but edges cross:
# e0: A(0,0)→C(1,1) diagonal
# e1: C(1,1)→B(1,0) right side
# e2: B(1,0)→D(0,1) diagonal — crosses e0 at (0.5, 0.5)
# e3: D(0,1)→A(0,0) left side
# This creates a bowtie/self-intersecting loop.
p_A = f.cartesian_point((0.0, 0.0, 0.0))  # (u=0, v=0)
p_B = f.cartesian_point((1.0, 0.0, 0.0))  # (u=1, v=0)
p_C = f.cartesian_point((1.0, 1.0, 0.0))  # (u=1, v=1)
p_D = f.cartesian_point((0.0, 1.0, 0.0))  # (u=0, v=1)

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
SQRT2 = math.sqrt(2.0)

# e0: A(0,0)→C(1,1) main diagonal — pcurve crosses e2 at (0.5,0.5)
e0 = mk_edge_line(v_A, v_C,
                  (0.0, 0.0, 0.0), (1.0, 1.0, 0.0), SQRT2,
                  (0.0, 0.0), (1.0, 1.0), SQRT2)
# e1: C(1,1)→B(1,0) right side
e1 = mk_edge_line(v_C, v_B,
                  (1.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (1.0, 1.0), (0.0, -1.0), 1.0)
# e2: B(1,0)→D(0,1) anti-diagonal — crosses e0 at (0.5,0.5)
e2 = mk_edge_line(v_B, v_D,
                  (1.0, 0.0, 0.0), (-1.0, 1.0, 0.0), SQRT2,
                  (1.0, 0.0), (-1.0, 1.0), SQRT2)
# e3: D(0,1)→A(0,0) left side
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry;
# self-intersecting diagonal pcurve boundary IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
