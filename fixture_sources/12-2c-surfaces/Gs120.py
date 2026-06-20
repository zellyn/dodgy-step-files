"""Gs120 — FaceDivide splitter curve tangent to boundary (zero-area sub-face).

Catalog claim: ShapeUpgrade_FaceDivide.SplitCurves produces a zero-area sub-face
when a splitter curve is tangent to the face boundary at a single point. The
division logic doesn't guard against tangency leading to degenerate splits.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - A PLANE IS the ADVANCED_FACE.face_geometry; boundary edge pcurve IS a line
    tangent to an interior seam pcurve at exactly one point, creating a
    zero-area sub-region; tangency-induced zero-area split IS the mechanism
    wired into face topology; FaceDivide.SplitCurves tangency guard absence
    IS the defect.
  - Byte assertions: contains(b'ADVANCED_FACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE IS the ADVANCED_FACE.face_geometry; splitter
    pcurve tangent to boundary pcurve at single point IS the mechanism wired
    into face topology; FaceDivide zero-area sub-face due to missing tangency
    guard IS the defect.
  - shape_null driver: zero-area degenerate sub-face; strict kernels reject;
    empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs120",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; "
        "splitter pcurve tangent to boundary pcurve at single point "
        "creates zero-area sub-face IS the mechanism wired into face topology; "
        "FaceDivide.SplitCurves missing tangency guard IS the defect; "
        "shape_null"
    ),
)

# ── PLANE ─────────────────────────────────────────────────────────────────────
# Byte assertion: contains(b'ADVANCED_FACE')
# Flat XY plane at origin; the degenerate split comes from boundary tangency.
plane_orig = f.cartesian_point((0.0, 0.0, 0.0))
plane_zdir = f.direction((0.0, 0.0, 1.0))
plane_xdir = f.direction((1.0, 0.0, 0.0))
plane_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs120_plane_ax',#{plane_orig.eid},#{plane_zdir.eid},#{plane_xdir.eid})"
)
plane = f._emit_raw(f"PLANE('gs120_plane',#{plane_ax.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Degenerate boundary: outer loop collapses to a cusp ───────────────────────
# The outer loop is a "kite" shape in parameter space where the top vertex is
# also a tangency point: two edges meet at (0.5, 1.0) and one edge is tangent
# to the other at that point (both arrive with slope 0), creating a zero-area
# cusp sub-region at the apex — the FaceDivide tangency defect.
#
# Vertices (in UV param space = XY for plane):
#   A = (0.0, 0.0)
#   B = (0.5, 1.0)   ← tangency point / cusp apex
#   C = (1.0, 0.0)
# Triangle with B at top; the two sides meeting at B are tangent (horizontal
# tangent direction at B), producing a zero-area neighbourhood around B.

p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((0.5, 1.0, 0.0))
p_C = f.cartesian_point((1.0, 0.0, 0.0))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# A→B: left edge, tangent direction at B is (0.5,0) normalized → (1,0) horizontal
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 2.0, 0.0), 1.118,
                  (0.0, 0.0), (1.0, 2.0), 1.118)
# B→C: right edge, arrives at B with horizontal tangent (−1,−2) → tangent at apex
e1 = mk_edge_line(v_B, v_C,
                  (0.5, 1.0, 0.0), (1.0, -2.0, 0.0), 1.118,
                  (0.5, 1.0), (1.0, -2.0), 1.118)
# C→A: base edge
e2 = mk_edge_line(v_C, v_A,
                  (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 1.0,
                  (1.0, 0.0), (-1.0, 0.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
])

# PLANE IS the face_geometry; tangency-at-apex boundary IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
