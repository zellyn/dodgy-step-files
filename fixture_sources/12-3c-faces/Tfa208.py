"""Tfa208 — FixSmallAreaWire undersized perimeter degenerate loop

Planar face with normal outer loop (10×10) plus inner loop with perimeter
≈0.0004 (area ≈1e-8). Tests wire-filtering threshold that removes sub-tolerance
loops from topology before face healing.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a PLANE. The outer boundary
is a 10×10 square loop. An inner wire is a tiny square with side length 1e-4
(perimeter ≈4e-4, area ≈1e-8) — below the OCCT FixSmallAreaWire detection
threshold. The code path at OCCT ShapeFix_Face lines 2483-2550 computes the
area of each inner wire and removes those falling below the tolerance threshold.
Without removal, the sub-tolerance inner loop propagates degenerate geometry
into downstream face classification, causing incorrect face topology output.
The undersized inner loop is the defect on the live traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa208",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on PLANE; "
        "outer boundary: 10×10 square (CCW); "
        "inner wire: tiny square side=1e-4 at center (5,5), "
        "perimeter≈4e-4, area≈1e-8 (below FixSmallAreaWire threshold); "
        "FixSmallAreaWire lines 2483-2550: area-threshold test removes sub-tolerance loops; "
        "without removal: degenerate loop propagates into downstream face classification; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── PLANE surface at origin, normal +Z ───────────────────────────────────────
plane = f.plane(f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
))

# ── Outer boundary: 10×10 square CCW ─────────────────────────────────────────
op_ll = f.cartesian_point(( 0.0,  0.0, 0.0))
op_lr = f.cartesian_point((10.0,  0.0, 0.0))
op_ur = f.cartesian_point((10.0, 10.0, 0.0))
op_ul = f.cartesian_point(( 0.0, 10.0, 0.0))

ov_ll = f.vertex_point(op_ll)
ov_lr = f.vertex_point(op_lr)
ov_ur = f.vertex_point(op_ur)
ov_ul = f.vertex_point(op_ul)

oe_bot = f.edge_curve(ov_ll, ov_lr, f.line(op_ll, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
oe_rgt = f.edge_curve(ov_lr, ov_ur, f.line(op_lr, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
oe_top = f.edge_curve(ov_ur, ov_ul, f.line(op_ur, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
oe_lft = f.edge_curve(ov_ul, ov_ll, f.line(op_ul, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

outer_loop = f.edge_loop([
    f.oriented_edge(oe_bot, True),
    f.oriented_edge(oe_rgt, True),
    f.oriented_edge(oe_top, True),
    f.oriented_edge(oe_lft, True),
])
outer_fob = f.face_outer_bound(outer_loop)

# ── Inner wire: tiny square 1e-4 × 1e-4 at center (5, 5) ─────────────────────
# perimeter = 4 * 1e-4 = 4e-4, area = 1e-8 (below threshold)
s = 1.0e-4
cx, cy = 5.0, 5.0

ip_ll = f.cartesian_point((cx,   cy,   0.0))
ip_lr = f.cartesian_point((cx+s, cy,   0.0))
ip_ur = f.cartesian_point((cx+s, cy+s, 0.0))
ip_ul = f.cartesian_point((cx,   cy+s, 0.0))

iv_ll = f.vertex_point(ip_ll)
iv_lr = f.vertex_point(ip_lr)
iv_ur = f.vertex_point(ip_ur)
iv_ul = f.vertex_point(ip_ul)

ie_bot = f.edge_curve(iv_ll, iv_lr, f.line(ip_ll, f.vector(f.direction(( 1.0, 0.0, 0.0)), s)))
ie_rgt = f.edge_curve(iv_lr, iv_ur, f.line(ip_lr, f.vector(f.direction(( 0.0, 1.0, 0.0)), s)))
ie_top = f.edge_curve(iv_ur, iv_ul, f.line(ip_ur, f.vector(f.direction((-1.0, 0.0, 0.0)), s)))
ie_lft = f.edge_curve(iv_ul, iv_ll, f.line(ip_ul, f.vector(f.direction(( 0.0,-1.0, 0.0)), s)))

inner_loop = f.edge_loop([
    f.oriented_edge(ie_bot, True),
    f.oriented_edge(ie_rgt, True),
    f.oriented_edge(ie_top, True),
    f.oriented_edge(ie_lft, True),
])
inner_fb = f.face_bound(inner_loop, False)

# ── Assemble face ─────────────────────────────────────────────────────────────
face = f.advanced_face([outer_fob, inner_fb], plane)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa208.stp")
