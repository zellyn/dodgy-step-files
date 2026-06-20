"""Tfa192 — ShapeAnalysis_CheckSmallFace.CheckPin three-way-pin-asymmetric

Face with three pins of different heights projecting from center into face.
Pin dimensions: (0.1×0.01), (0.2×0.005), (0.1×0.002) units. CheckPin reports
largest pin (0.2×0.005) only, missing the two smaller pins due to early-exit
logic that doesn't aggregate all singularities.

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE on a PLANE. Outer boundary is a
1×1 square. Three inner rectangular pin wires project from the interior toward
center, each touching the outer boundary on one side. The CheckPin heuristic
uses early-exit on finding the largest pin, missing the two smaller ones.
Defect IS on live face traversal path.

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
    catalog_id="Tfa192",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on PLANE (1×1); "
        "outer boundary: unit square at (0,0)-(1,1); "
        "3 inner pin wires: "
        "  pin1 (0.1×0.01) at left edge touching (0, 0.5); "
        "  pin2 (0.2×0.005) at bottom edge touching (0.5, 0) [largest pin]; "
        "  pin3 (0.1×0.002) at right edge touching (1.0, 0.7); "
        "CheckPin early-exit on largest pin (pin2), misses pin1 and pin3; "
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

# ── Pin 1: 0.1×0.01 at left edge, touches (0, 0.5) ─────────────────────────
# Rectangle from (0, 0.495) to (0.1, 0.505); left edge touches outer boundary
p1_lo = f.cartesian_point((0.0,  0.495, 0.0))  # left-bottom (on outer edge)
p1_ro = f.cartesian_point((0.0,  0.505, 0.0))  # left-top    (on outer edge)
p1_ri = f.cartesian_point((0.1,  0.505, 0.0))  # right-top   (inner)
p1_li = f.cartesian_point((0.1,  0.495, 0.0))  # right-bottom (inner)

v1_lo = f.vertex_point(p1_lo)
v1_ro = f.vertex_point(p1_ro)
v1_ri = f.vertex_point(p1_ri)
v1_li = f.vertex_point(p1_li)

p1_e1 = _line_edge(p1_lo, v1_lo, p1_li, v1_li)  # bottom (→)
p1_e2 = _line_edge(p1_li, v1_li, p1_ri, v1_ri)  # right (↑)
p1_e3 = _line_edge(p1_ri, v1_ri, p1_ro, v1_ro)  # top (←)
p1_e4 = _line_edge(p1_ro, v1_ro, p1_lo, v1_lo)  # left (↓) — touches outer

inner_loop1 = f.edge_loop([
    f.oriented_edge(p1_e1, True), f.oriented_edge(p1_e2, True),
    f.oriented_edge(p1_e3, True), f.oriented_edge(p1_e4, True),
])
inner_fb1 = f.face_bound(inner_loop1, False)

# ── Pin 2: 0.2×0.005 at bottom edge, touches (0.5, 0) ───────────────────────
# Rectangle from (0.45, 0) to (0.65, 0.005); bottom edge touches outer boundary
p2_ll = f.cartesian_point((0.45, 0.0,   0.0))  # left-bottom (on outer edge)
p2_lr = f.cartesian_point((0.65, 0.0,   0.0))  # right-bottom (on outer edge)
p2_ur = f.cartesian_point((0.65, 0.005, 0.0))  # right-top
p2_ul = f.cartesian_point((0.45, 0.005, 0.0))  # left-top

v2_ll = f.vertex_point(p2_ll)
v2_lr = f.vertex_point(p2_lr)
v2_ur = f.vertex_point(p2_ur)
v2_ul = f.vertex_point(p2_ul)

p2_e1 = _line_edge(p2_ll, v2_ll, p2_lr, v2_lr)  # bottom (→)
p2_e2 = _line_edge(p2_lr, v2_lr, p2_ur, v2_ur)  # right (↑)
p2_e3 = _line_edge(p2_ur, v2_ur, p2_ul, v2_ul)  # top (←)
p2_e4 = _line_edge(p2_ul, v2_ul, p2_ll, v2_ll)  # left (↓)

inner_loop2 = f.edge_loop([
    f.oriented_edge(p2_e1, True), f.oriented_edge(p2_e2, True),
    f.oriented_edge(p2_e3, True), f.oriented_edge(p2_e4, True),
])
inner_fb2 = f.face_bound(inner_loop2, False)

# ── Pin 3: 0.1×0.002 at right edge, touches (1.0, 0.7) ──────────────────────
# Rectangle from (0.9, 0.699) to (1.0, 0.701); right edge touches outer boundary
p3_rlo = f.cartesian_point((1.0,  0.699, 0.0))  # right-bottom (on outer edge)
p3_rhi = f.cartesian_point((1.0,  0.701, 0.0))  # right-top    (on outer edge)
p3_lhi = f.cartesian_point((0.9,  0.701, 0.0))  # left-top
p3_llo = f.cartesian_point((0.9,  0.699, 0.0))  # left-bottom

v3_rlo = f.vertex_point(p3_rlo)
v3_rhi = f.vertex_point(p3_rhi)
v3_lhi = f.vertex_point(p3_lhi)
v3_llo = f.vertex_point(p3_llo)

p3_e1 = _line_edge(p3_rlo, v3_rlo, p3_llo, v3_llo)  # bottom (←)
p3_e2 = _line_edge(p3_llo, v3_llo, p3_lhi, v3_lhi)  # left (↑)
p3_e3 = _line_edge(p3_lhi, v3_lhi, p3_rhi, v3_rhi)  # top (→)
p3_e4 = _line_edge(p3_rhi, v3_rhi, p3_rlo, v3_rlo)  # right (↓) — touches outer

inner_loop3 = f.edge_loop([
    f.oriented_edge(p3_e1, True), f.oriented_edge(p3_e2, True),
    f.oriented_edge(p3_e3, True), f.oriented_edge(p3_e4, True),
])
inner_fb3 = f.face_bound(inner_loop3, False)

# ── Assemble face ─────────────────────────────────────────────────────────────
face = f.advanced_face([outer_fob, inner_fb1, inner_fb2, inner_fb3], plane)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa192.stp")
