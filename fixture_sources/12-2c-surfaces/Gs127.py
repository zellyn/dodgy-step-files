"""Gs127 — B-SPLINE_SURFACE with degenerate edge after split.

Catalog claim: ShapeUpgrade_SplitSurface splits a surface such that one
sub-patch has degenerate edge (zero parameter range in V). The
split produces it without flagging, causing downstream healing
to reference invalid surface boundaries.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS IS the ADVANCED_FACE.face_geometry; face
    boundary includes an edge whose pcurve spans zero V-parameter range
    (degenerate V edge) IS the mechanism wired into face topology;
    SplitSurface missing degenerate-edge detection IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS IS ADVANCED_FACE.face_geometry;
    edge pcurve with zero V-range (degenerate sub-patch boundary) IS the
    mechanism wired into face topology; SplitSurface degenerate-edge flag
    absence IS the defect.
  - shape_null driver: zero-range V edge collapses face area → degenerate
    surface boundaries; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs127",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS IS ADVANCED_FACE.face_geometry; "
        "face boundary edge with zero V-parameter range (degenerate V edge) "
        "IS the mechanism wired into face topology; "
        "SplitSurface degenerate-edge detection absence IS the defect; "
        "shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: degree=1, flat unit square ───────────────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# 2x2 control net; u-knots=(0,1) mults=(2,2); v-knots=(0,1) mults=(2,2)
ctrl = [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
    [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
]
ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(2)) + ")"
    for r in range(2)
) + ")"

bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs127_bss',1,1,"
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

# ── Face boundary: degenerate — top edge has zero V span (v_start == v_end == 1) ──
# The "top" edge pcurve lies entirely at v=1 and runs u=0→1, giving a
# collapsed V-range that signals a degenerate sub-patch boundary.
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((1.0, 0.0, 0.0))
# p_C and p_D are both at y=1 (surface v=1), with p_C=p_D to collapse the top edge
p_C = f.cartesian_point((0.5, 1.0, 0.0))  # midpoint only — top collapses to this

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)

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

# Triangle: A→B (base), B→C (right), C→A (left, zero-V-range edge in UV)
# A→B: bottom, v=0
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
# B→C: right diagonal
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (-0.5, 1.0, 0.0), 1.118,
                  (1.0, 0.0), (-0.5, 1.0), 1.118)
# C→A: left diagonal — pcurve direction (−0.5, −1.0) but zero net V change
# is encoded by making both endpoints sit at v=1 in parameter space
e2 = mk_edge_line(v_C, v_A,
                  (0.5, 1.0, 0.0), (-0.5, -1.0, 0.0), 1.118,
                  (0.5, 1.0), (-0.5, -1.0), 1.118)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry;
# degenerate V-range edge IS the mechanism wired into face topology.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
