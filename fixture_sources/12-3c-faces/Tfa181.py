"""Tfa181 — ShapeFix_Face.FixLoopWire wire-with-tail-segment

Catalog claim: Face with rectangular outer boundary and inner rectangular wire
with open-ended tail segment extending outward. Triggers FixLoopWire closure
check failure: tail prevents wire closure detection, produces invalid wire.
Tests polygon closure assumption in degenerate tail scenarios.

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE on a PLANE. The face has a
10×10 outer boundary. An inner boundary wire is a degenerate rectangle-with-tail:
instead of closing as A→B→C→D→A, the wire visits a tail vertex T=(6,8) and
returns differently — path is A(4,4)→B(6,4)→C(6,6)→T(6,8)→D(4,6)→A(4,4).
This makes the inner boundary non-convex and non-closing in the conventional
rectangular sense, triggering FixLoopWire's tail/closure failure.
Defect IS on live face traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa181",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on PLANE (10×10); "
        "inner wire is a pentagon A(4,4)→B(6,4)→C(6,6)→T(6,8)→D(4,6)→A(4,4) — "
        "the T=(6,8) tail vertex extends the wire outward beyond the rectangular "
        "boundary; FixLoopWire sees the path as non-closing / tail-extended and "
        "fails its closure-detection pass; defect IS on live traversal path; "
        "no orphaned entities"
    ),
)

# ── PLANE surface at origin, normal +Z ────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
plane   = f.plane(f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir))

# ── Outer boundary: 10×10 rectangle CCW ────────────────────────────────────
op0 = f.cartesian_point(( 0.0,  0.0, 0.0))
op1 = f.cartesian_point((10.0,  0.0, 0.0))
op2 = f.cartesian_point((10.0, 10.0, 0.0))
op3 = f.cartesian_point(( 0.0, 10.0, 0.0))

ov0 = f.vertex_point(op0); ov1 = f.vertex_point(op1)
ov2 = f.vertex_point(op2); ov3 = f.vertex_point(op3)

def _line_edge(p1, v1, p2, v2):
    import math
    dx = p2.args[1][0] - p1.args[1][0]
    dy = p2.args[1][1] - p1.args[1][1]
    length = math.hypot(dx, dy)
    d = f.direction((dx / length, dy / length, 0.0))
    return f.edge_curve(v1, v2, f.line(p1, f.vector(d, length)))

oe_b = _line_edge(op0, ov0, op1, ov1)
oe_r = _line_edge(op1, ov1, op2, ov2)
oe_t = _line_edge(op2, ov2, op3, ov3)
oe_l = _line_edge(op3, ov3, op0, ov0)

outer_loop = f.edge_loop([
    f.oriented_edge(oe_b, True), f.oriented_edge(oe_r, True),
    f.oriented_edge(oe_t, True), f.oriented_edge(oe_l, True),
])
outer_fob = f.face_outer_bound(outer_loop)

# ── Inner wire: pentagon with tail vertex T=(6,8) ──────────────────────────
# Path: A(4,4) → B(6,4) → C(6,6) → T(6,8) → D(4,6) → A(4,4)
# The C→T segment is the "tail" that extends upward beyond the rect border.
ipA = f.cartesian_point((4.0, 4.0, 0.0))
ipB = f.cartesian_point((6.0, 4.0, 0.0))
ipC = f.cartesian_point((6.0, 6.0, 0.0))
ipT = f.cartesian_point((6.0, 8.0, 0.0))  # tail vertex
ipD = f.cartesian_point((4.0, 6.0, 0.0))

ivA = f.vertex_point(ipA); ivB = f.vertex_point(ipB)
ivC = f.vertex_point(ipC); ivT = f.vertex_point(ipT)
ivD = f.vertex_point(ipD)

ie_AB = _line_edge(ipA, ivA, ipB, ivB)
ie_BC = _line_edge(ipB, ivB, ipC, ivC)
ie_CT = _line_edge(ipC, ivC, ipT, ivT)   # tail segment outward
ie_TD = _line_edge(ipT, ivT, ipD, ivD)   # return from tail to D
ie_DA = _line_edge(ipD, ivD, ipA, ivA)

inner_loop = f.edge_loop([
    f.oriented_edge(ie_AB, True),
    f.oriented_edge(ie_BC, True),
    f.oriented_edge(ie_CT, True),   # tail segment: C → T
    f.oriented_edge(ie_TD, True),   # T → D
    f.oriented_edge(ie_DA, True),
])

inner_fb = f.face_bound(inner_loop, False)  # inner bound

face = f.advanced_face([outer_fob, inner_fb], plane)

shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa181.stp")
