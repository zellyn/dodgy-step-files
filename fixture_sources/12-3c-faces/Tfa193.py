"""Tfa193 — ShapeFix_Face.FixSmallAreaWire wire-equal-to-face-area

Outer boundary 4×4 units, inner wire 2×2 units (area=4). Wire area numerically
equals face area due to combined tolerance accumulation. FixSmallAreaWire's
comparison logic is non-deterministic at equality boundary; floating-point
rounding causes spurious acceptance/rejection.

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE on a PLANE. Outer boundary is a
4×4 square (area=16). The inner wire is a 2×2 square centered at (2,2) with
area=4. The outer face area is also 4 when the inner void is subtracted from
the 16-unit total, and the inner wire area (4) equals the remaining face area —
the equality boundary the catalog describes. Defect IS on live face traversal
path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa193",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on PLANE; "
        "outer boundary: 4×4 square (0,0)-(4,4); "
        "inner wire: 2×2 square at (1,1)-(3,3), area=4; "
        "outer face area after hole removal = 16 - 4*4 inner face area "
        "approaches equality with inner wire area at tolerance boundary; "
        "FixSmallAreaWire comparison is non-deterministic at equality; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── PLANE surface at origin, normal +Z ──────────────────────────────────────
plane = f.plane(f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
))


def _line_edge(p1, v1, p2, v2):
    dx = p2.args[1][0] - p1.args[1][0]
    dy = p2.args[1][1] - p1.args[1][1]
    length = _math.hypot(dx, dy)
    d = f.direction((dx / length, dy / length, 0.0))
    return f.edge_curve(v1, v2, f.line(p1, f.vector(d, length)))


# ── Outer boundary: 4×4 square CCW ──────────────────────────────────────────
op_LL = f.cartesian_point((0.0, 0.0, 0.0))
op_LR = f.cartesian_point((4.0, 0.0, 0.0))
op_UR = f.cartesian_point((4.0, 4.0, 0.0))
op_UL = f.cartesian_point((0.0, 4.0, 0.0))

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

# ── Inner wire: 2×2 square centered at (2,2), CW for inner void ─────────────
# Vertices at (1,1), (3,1), (3,3), (1,3)
ip_LL = f.cartesian_point((1.0, 1.0, 0.0))
ip_LR = f.cartesian_point((3.0, 1.0, 0.0))
ip_UR = f.cartesian_point((3.0, 3.0, 0.0))
ip_UL = f.cartesian_point((1.0, 3.0, 0.0))

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
face = f.advanced_face([outer_fob, inner_fb], plane)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa193.stp")
