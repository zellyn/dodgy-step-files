"""Tfa194 — ShapeAnalysis_CheckSmallFace.CheckSpotFace face-with-bbox-much-larger

Outer boundary 200×200 units with inner rectangle 100×100 units (50-150 on
each axis), but placement yields bounding box extrapolation to full outer
extent. CheckSpotFace's 3D bbox-based heuristic misclassifies tight inner
geometry as spot-like due to bbox >> actual face extent.

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE on a PLANE. Outer boundary is a
200×200 square. Inner void is a 100×100 square from (50,50) to (150,150).
The bounding box spans the full 200×200 extent while the actual face geometry
(the annular ring) has a smaller effective area. CheckSpotFace bbox heuristic
sees bbox(200×200) >> face_area(30000) and misclassifies the face as a
degenerate spot. Defect IS on live face traversal path.

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
    catalog_id="Tfa194",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on PLANE; "
        "outer boundary: 200×200 square (0,0)-(200,200); "
        "inner void: 100×100 square at (50,50)-(150,150); "
        "face bbox = 200×200 >> actual face ring area = 30000; "
        "CheckSpotFace 3D bbox heuristic misclassifies annular ring as spot; "
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


# ── Outer boundary: 200×200 square CCW ──────────────────────────────────────
op_LL = f.cartesian_point((  0.0,   0.0, 0.0))
op_LR = f.cartesian_point((200.0,   0.0, 0.0))
op_UR = f.cartesian_point((200.0, 200.0, 0.0))
op_UL = f.cartesian_point((  0.0, 200.0, 0.0))

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

# ── Inner void: 100×100 square centered in outer (50,50)-(150,150) ──────────
ip_LL = f.cartesian_point(( 50.0,  50.0, 0.0))
ip_LR = f.cartesian_point((150.0,  50.0, 0.0))
ip_UR = f.cartesian_point((150.0, 150.0, 0.0))
ip_UL = f.cartesian_point(( 50.0, 150.0, 0.0))

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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa194.stp")
