"""Tfa191 — ShapeFix_Face.FixLoopWire with-multiple-inner-loops-touching

Catalog claim: Face with 3 rectangular inner wires (0.2×0.15, 0.2×0.05,
0.2×0.15 units) positioned at distinct vertices of outer 1×1 square. All inner
loops touch outer boundary at single vertices; FixLoopWire processes sequentially
with ownership cascading. Defect: wire reordering cascades corruption when
processing 2nd and 3rd inner wires due to improper edge-ownership tracking
across loop merges.

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE on a PLANE. Outer boundary is a
1×1 square. Three inner rectangular loops are positioned at three corners of
the outer square (lower-left, lower-right, upper-left), each touching the
outer boundary at exactly one corner vertex. FixLoopWire processes each inner
wire in sequence; after merging the first wire, internal edge-ownership tables
are corrupted, causing incorrect results when processing subsequent inner wires.
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
    catalog_id="Tfa191",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on PLANE (1×1); "
        "outer boundary: unit square at (0,0)-(1,1); "
        "3 inner wires at corners: "
        "  inner1 (0.2×0.15) at lower-left touching vertex (0,0); "
        "  inner2 (0.2×0.05) at lower-right touching vertex (1,0); "
        "  inner3 (0.2×0.15) at upper-left touching vertex (0,1); "
        "FixLoopWire processes inner wires sequentially; edge-ownership tracking "
        "corrupted after first merge, cascading to 2nd and 3rd inner wires; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── PLANE surface at origin, normal +Z ────────────────────────────────────
plane = f.plane(f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
))

# ── Helper for line edges ─────────────────────────────────────────────────
def _line_edge(p1, v1, p2, v2):
    dx = p2.args[1][0] - p1.args[1][0]
    dy = p2.args[1][1] - p1.args[1][1]
    length = _math.hypot(dx, dy)
    d = f.direction((dx/length, dy/length, 0.0))
    return f.edge_curve(v1, v2, f.line(p1, f.vector(d, length)))

# ── Outer boundary: 1×1 square CCW ─────────────────────────────────────────
op_LL = f.cartesian_point((0.0, 0.0, 0.0))   # lower-left
op_LR = f.cartesian_point((1.0, 0.0, 0.0))   # lower-right
op_UR = f.cartesian_point((1.0, 1.0, 0.0))   # upper-right
op_UL = f.cartesian_point((0.0, 1.0, 0.0))   # upper-left

# Use shared vertex points at the touching corners
ov_LL = f.vertex_point(op_LL)
ov_LR = f.vertex_point(op_LR)
ov_UR = f.vertex_point(op_UR)
ov_UL = f.vertex_point(op_UL)

oe_b = _line_edge(op_LL, ov_LL, op_LR, ov_LR)  # bottom
oe_r = _line_edge(op_LR, ov_LR, op_UR, ov_UR)  # right
oe_t = _line_edge(op_UR, ov_UR, op_UL, ov_UL)  # top
oe_l = _line_edge(op_UL, ov_UL, op_LL, ov_LL)  # left

outer_loop = f.edge_loop([
    f.oriented_edge(oe_b, True), f.oriented_edge(oe_r, True),
    f.oriented_edge(oe_t, True), f.oriented_edge(oe_l, True),
])
outer_fob = f.face_outer_bound(outer_loop)

# ── Inner wire 1: 0.2×0.15 at lower-left, corner touches (0,0) ────────────
# Rectangle: (0,0) → (0.2,0) → (0.2,0.15) → (0,0.15) → (0,0)
# Touch point: lower-left vertex (0,0) = ov_LL (shared)
i1_p1 = op_LL                               # shared with outer
i1_p2 = f.cartesian_point((0.20, 0.00, 0.0))
i1_p3 = f.cartesian_point((0.20, 0.15, 0.0))
i1_p4 = f.cartesian_point((0.00, 0.15, 0.0))

i1_v1 = ov_LL                              # shared vertex (touch point)
i1_v2 = f.vertex_point(i1_p2)
i1_v3 = f.vertex_point(i1_p3)
i1_v4 = f.vertex_point(i1_p4)

i1_e1 = _line_edge(i1_p1, i1_v1, i1_p2, i1_v2)
i1_e2 = _line_edge(i1_p2, i1_v2, i1_p3, i1_v3)
i1_e3 = _line_edge(i1_p3, i1_v3, i1_p4, i1_v4)
i1_e4 = _line_edge(i1_p4, i1_v4, i1_p1, i1_v1)

inner_loop1 = f.edge_loop([
    f.oriented_edge(i1_e1, True), f.oriented_edge(i1_e2, True),
    f.oriented_edge(i1_e3, True), f.oriented_edge(i1_e4, True),
])
inner_fb1 = f.face_bound(inner_loop1, False)

# ── Inner wire 2: 0.2×0.05 at lower-right, corner touches (1,0) ───────────
# Rectangle: (1,0) → (0.8,0) → (0.8,0.05) → (1,0.05) → (1,0)
# Touch point: lower-right vertex (1,0) = ov_LR (shared)
i2_p1 = op_LR                               # shared with outer
i2_p2 = f.cartesian_point((0.80, 0.00, 0.0))
i2_p3 = f.cartesian_point((0.80, 0.05, 0.0))
i2_p4 = f.cartesian_point((1.00, 0.05, 0.0))

i2_v1 = ov_LR                              # shared vertex (touch point)
i2_v2 = f.vertex_point(i2_p2)
i2_v3 = f.vertex_point(i2_p3)
i2_v4 = f.vertex_point(i2_p4)

i2_e1 = _line_edge(i2_p1, i2_v1, i2_p2, i2_v2)
i2_e2 = _line_edge(i2_p2, i2_v2, i2_p3, i2_v3)
i2_e3 = _line_edge(i2_p3, i2_v3, i2_p4, i2_v4)
i2_e4 = _line_edge(i2_p4, i2_v4, i2_p1, i2_v1)

inner_loop2 = f.edge_loop([
    f.oriented_edge(i2_e1, True), f.oriented_edge(i2_e2, True),
    f.oriented_edge(i2_e3, True), f.oriented_edge(i2_e4, True),
])
inner_fb2 = f.face_bound(inner_loop2, False)

# ── Inner wire 3: 0.2×0.15 at upper-left, corner touches (0,1) ───────────
# Rectangle: (0,1) → (0.2,1) → (0.2,0.85) → (0,0.85) → (0,1)
# Touch point: upper-left vertex (0,1) = ov_UL (shared)
i3_p1 = op_UL                               # shared with outer
i3_p2 = f.cartesian_point((0.20, 1.00, 0.0))
i3_p3 = f.cartesian_point((0.20, 0.85, 0.0))
i3_p4 = f.cartesian_point((0.00, 0.85, 0.0))

i3_v1 = ov_UL                              # shared vertex (touch point)
i3_v2 = f.vertex_point(i3_p2)
i3_v3 = f.vertex_point(i3_p3)
i3_v4 = f.vertex_point(i3_p4)

i3_e1 = _line_edge(i3_p1, i3_v1, i3_p2, i3_v2)
i3_e2 = _line_edge(i3_p2, i3_v2, i3_p3, i3_v3)
i3_e3 = _line_edge(i3_p3, i3_v3, i3_p4, i3_v4)
i3_e4 = _line_edge(i3_p4, i3_v4, i3_p1, i3_v1)

inner_loop3 = f.edge_loop([
    f.oriented_edge(i3_e1, True), f.oriented_edge(i3_e2, True),
    f.oriented_edge(i3_e3, True), f.oriented_edge(i3_e4, True),
])
inner_fb3 = f.face_bound(inner_loop3, False)

# ── Assemble face ─────────────────────────────────────────────────────────
face = f.advanced_face([outer_fob, inner_fb1, inner_fb2, inner_fb3], plane)

shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa191.stp")
