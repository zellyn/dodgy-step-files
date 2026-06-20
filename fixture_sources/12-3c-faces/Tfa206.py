"""Tfa206 — FixOrientation TinyWireFiltering single-edge degenerate

Planar square face with outer loop (5×5) plus single-edge near-degenerate inner
loop (length 1e-8). Tests wire-filtering branch that segregates sub-precision
loops into VerySmallWires before orientation analysis.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a PLANE. The outer boundary
is a 5×5 square loop. A second (inner) wire consists of a single closed edge
whose length is 1e-8 — far below the OCCT wire tolerance threshold. The
FixOrientation code path at lines 1185-1225 calls TinyWireFiltering, which
segregates sub-precision loops into a VerySmallWires list before running
containment tests. Without segregation, the degenerate single-edge inner loop
produces a false vertex state that corrupts the orientation classifier. The
near-zero length edge is the defect on the live traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa206",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on PLANE; "
        "outer boundary: 5×5 square (CCW); "
        "inner wire: single closed edge at (2.5, 2.5) with length=1e-8 "
        "(degenerate: far below wire-tolerance threshold); "
        "FixOrientation TinyWireFiltering lines 1185-1225: segregates "
        "sub-precision loops into VerySmallWires before orientation analysis; "
        "degenerate single-edge inner loop creates false vertex state; "
        "without segregation, false vertex state corrupts containment classifier; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── PLANE surface at origin, normal +Z ───────────────────────────────────────
plane = f.plane(f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
))

# ── Outer boundary: 5×5 square CCW ───────────────────────────────────────────
op_ll = f.cartesian_point((0.0, 0.0, 0.0))
op_lr = f.cartesian_point((5.0, 0.0, 0.0))
op_ur = f.cartesian_point((5.0, 5.0, 0.0))
op_ul = f.cartesian_point((0.0, 5.0, 0.0))

ov_ll = f.vertex_point(op_ll)
ov_lr = f.vertex_point(op_lr)
ov_ur = f.vertex_point(op_ur)
ov_ul = f.vertex_point(op_ul)

oe_bot = f.edge_curve(ov_ll, ov_lr, f.line(op_ll, f.vector(f.direction(( 1.0, 0.0, 0.0)), 5.0)))
oe_rgt = f.edge_curve(ov_lr, ov_ur, f.line(op_lr, f.vector(f.direction(( 0.0, 1.0, 0.0)), 5.0)))
oe_top = f.edge_curve(ov_ur, ov_ul, f.line(op_ur, f.vector(f.direction((-1.0, 0.0, 0.0)), 5.0)))
oe_lft = f.edge_curve(ov_ul, ov_ll, f.line(op_ul, f.vector(f.direction(( 0.0,-1.0, 0.0)), 5.0)))

outer_loop = f.edge_loop([
    f.oriented_edge(oe_bot, True),
    f.oriented_edge(oe_rgt, True),
    f.oriented_edge(oe_top, True),
    f.oriented_edge(oe_lft, True),
])
outer_fob = f.face_outer_bound(outer_loop)

# ── Inner wire: single closed degenerate edge, length ≈ 1e-8 ─────────────────
# Placed at center (2.5, 2.5) — tiny closed line segment
tiny_len = 1.0e-8
ip_start = f.cartesian_point((2.5, 2.5, 0.0))
iv_start = f.vertex_point(ip_start)
# Closed edge: start==end vertex, degenerate length
tiny_edge = f.edge_curve(
    iv_start, iv_start,
    f.line(ip_start, f.vector(f.direction((1.0, 0.0, 0.0)), tiny_len)),
)

inner_loop = f.edge_loop([
    f.oriented_edge(tiny_edge, True),
])
inner_fb = f.face_bound(inner_loop, False)

# ── Assemble face ─────────────────────────────────────────────────────────────
face = f.advanced_face([outer_fob, inner_fb], plane)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa206.stp")
