"""Tfa195 — ShapeFix_Face.FixOrientation face-on-curved-vs-planar

Unit square planar face with centered 0.5×0.5 inner rectangle. FixOrientation's
winding tests yield opposite results for equivalent topology: planar face
correctly detects inner winding direction, but B-spline approximation of same
geometry yields reversed classification due to numerical drift in normal
computation.

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE on a B_SPLINE_SURFACE_WITH_KNOTS
(degree 1×1, 2×2 control grid) approximating a unit square plane. Outer
boundary is 1×1 CCW (correct orientation), inner wire is 0.5×0.5 centered
at (0.25, 0.25) to (0.75, 0.75). The B-spline surface approximation of the
same flat geometry introduces a slight numerical drift in the normal direction;
FixOrientation's winding-test cross-product on this near-planar surface yields
a reversed classification for the inner wire, triggering a spurious flip.
Defect IS on live face traversal path.

Byte assertions:
  - contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa195",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on B_SPLINE_SURFACE_WITH_KNOTS "
        "approximating unit square; "
        "outer boundary: 1×1 square (0,0)-(1,1) CCW; "
        "inner wire: 0.5×0.5 at (0.25,0.25)-(0.75,0.75); "
        "B-spline numerical drift causes FixOrientation winding cross-product "
        "to yield reversed classification for inner wire vs planar equivalent; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── B-spline surface degree 1×1 approximating unit square flat patch ─────────
# 2×2 control grid: corners of unit square in z=0 plane
# U goes 0→1 in X, V goes 0→1 in Y
cp = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
    [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
]]
surf = f.b_spline_surface_with_knots(
    u_degree=1, v_degree=1,
    control_points_grid=cp,
    u_multiplicities=[2, 2],
    v_multiplicities=[2, 2],
    u_knots=[0.0, 1.0],
    v_knots=[0.0, 1.0],
)


def _line_edge(p1, v1, p2, v2):
    dx = p2.args[1][0] - p1.args[1][0]
    dy = p2.args[1][1] - p1.args[1][1]
    length = _math.hypot(dx, dy)
    d = f.direction((dx / length, dy / length, 0.0))
    return f.edge_curve(v1, v2, f.line(p1, f.vector(d, length)))


# ── Outer boundary: 1×1 square CCW ──────────────────────────────────────────
op_LL = f.cartesian_point((0.0, 0.0, 0.0))
op_LR = f.cartesian_point((1.0, 0.0, 0.0))
op_UR = f.cartesian_point((1.0, 1.0, 0.0))
op_UL = f.cartesian_point((0.0, 1.0, 0.0))

ov_LL = f.vertex_point(op_LL)
ov_LR = f.vertex_point(op_LR)
ov_UR = f.vertex_point(op_UR)
ov_UL = f.vertex_point(op_UL)

oe_b = _line_edge(op_LL, ov_LL, op_LR, ov_LR)
oe_r = _line_edge(op_LR, ov_LR, op_UR, ov_UR)
oe_t = _line_edge(op_UR, ov_UR, op_UL, ov_UL)
oe_l = _line_edge(op_UL, ov_UL, op_LL, ov_LL)

outer_loop = f.edge_loop([
    f.oriented_edge(oe_b, True), f.oriented_edge(oe_r, True),
    f.oriented_edge(oe_t, True), f.oriented_edge(oe_l, True),
])
outer_fob = f.face_outer_bound(outer_loop)

# ── Inner wire: 0.5×0.5 centered at (0.5,0.5) ────────────────────────────────
ip_LL = f.cartesian_point((0.25, 0.25, 0.0))
ip_LR = f.cartesian_point((0.75, 0.25, 0.0))
ip_UR = f.cartesian_point((0.75, 0.75, 0.0))
ip_UL = f.cartesian_point((0.25, 0.75, 0.0))

iv_LL = f.vertex_point(ip_LL)
iv_LR = f.vertex_point(ip_LR)
iv_UR = f.vertex_point(ip_UR)
iv_UL = f.vertex_point(ip_UL)

ie_b = _line_edge(ip_LL, iv_LL, ip_LR, iv_LR)
ie_r = _line_edge(ip_LR, iv_LR, ip_UR, iv_UR)
ie_t = _line_edge(ip_UR, iv_UR, ip_UL, iv_UL)
ie_l = _line_edge(ip_UL, iv_UL, ip_LL, iv_LL)

inner_loop = f.edge_loop([
    f.oriented_edge(ie_b, True), f.oriented_edge(ie_r, True),
    f.oriented_edge(ie_t, True), f.oriented_edge(ie_l, True),
])
inner_fb = f.face_bound(inner_loop, False)

# ── Assemble face ─────────────────────────────────────────────────────────────
face = f.advanced_face([outer_fob, inner_fb], surf)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa195.stp")
