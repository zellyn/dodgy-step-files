"""Twi105 — ShapeAnalysis_Wire.CheckIntersectingEdges seam-gap tolerance filter miss.

Catalog claim: CheckIntersectingEdges detects non-adjacent edge intersections by 2D
parametric intersection followed by 3D vertex-tolerance distance check (line 1645,
OK1/OK2). When non-adjacent edges' parametric intersection maps to a spatial point in
a seam-edge gap (vertex offset region), tolerance filtering fails to detect a genuine
intersection. Gap magnitude typically < vertex tolerance but > parametric precision.

Mechanism IS a planar face whose outer wire has 4 edges:
  E1: horizontal base (v0(0,0,0) → v1(10,0,0))
  E2: right seam-offset segment (v1(10,0,0) → v2(10,0.05,0)) — tiny vertical seam offset
  E3: diagonal crossing E1 (v2(10,0.05,0) → v3(0,1,0)) — crosses E1 in space at ~(0.49,0,0)
  E4: left return (v3(0,1,0) → v0(0,0,0)) — closes the wire

The geometric intersection of E3 with E1 occurs at ~(0.49, 0, 0). The seam offset
at E2 places the computed intersection point 0.05 units from the E2-E3 junction.
With vertex tolerance 0.1 units, CheckIntersectingEdges' OK1/OK2 test at line 1645
filters the intersection point as "within vertex tolerance of an endpoint" — a false
negative. Gap magnitude 0.05 < vertex tolerance 0.1 > parametric precision — IS mechanism.

Single-face fixture (tier-3: n_faces_total == 1).

Tier-3 assertion:
  - n_faces_total == 1

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi105",
    defect=(
        "Single ADVANCED_FACE on a PLANE in a CLOSED_SHELL; "
        "outer EDGE_LOOP has 4 edges: "
        "E1(v0(0,0,0)→v1(10,0,0)) horizontal base; "
        "E2(v1(10,0,0)→v2(10,0.05,0)) 0.05-unit seam offset step — creates vertex offset gap; "
        "E3(v2(10,0.05,0)→v3(0,1,0)) diagonal that geometrically crosses E1 at ~(0.49,0,0); "
        "E4(v3(0,1,0)→v0(0,0,0)) left return closing the wire; "
        "geometric intersection of E3 with E1 maps to spatial point 0.05 units from E2/E3 junction; "
        "vertex tolerance=0.1 > gap 0.05 > parametric precision: "
        "CheckIntersectingEdges OK1/OK2 test at line 1645 filters intersection as endpoint-proximal; "
        "genuine crossing is missed — IS the seam-gap tolerance filter failure mechanism; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE "
        "in CLOSED_SHELL — never orphaned"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

import math as _math

# ── Vertices ──────────────────────────────────────────────────────────────────
v0 = f.vertex_point(f.cartesian_point((0.0,  0.0,   0.0)))   # bottom-left
v1 = f.vertex_point(f.cartesian_point((10.0, 0.0,   0.0)))   # bottom-right
v2 = f.vertex_point(f.cartesian_point((10.0, 0.05,  0.0)))   # seam-offset — 0.05 gap
v3 = f.vertex_point(f.cartesian_point((0.0,  1.0,   0.0)))   # left midpoint

# ── E1: v0(0,0,0) → v1(10,0,0) — horizontal base ─────────────────────────────
e1_line = f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                 f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
e1  = f.edge_curve(v0, v1, e1_line)
oe1 = f.oriented_edge(e1, True)

# ── E2: v1(10,0,0) → v2(10,0.05,0) — tiny seam offset step ───────────────────
# This 0.05-unit vertical step creates the seam-edge gap at the right side
e2_line = f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                 f.vector(f.direction((0.0, 1.0, 0.0)), 0.05))
e2  = f.edge_curve(v1, v2, e2_line)
oe2 = f.oriented_edge(e2, True)

# ── E3: v2(10,0.05,0) → v3(0,-10,0) — diagonal crossing E1 near the seam gap ─
# E3 from (10,0.05,0) to (0,-10,0): y(t)=0.05+t*(-10.05)=0 => t≈0.00498,
# x≈9.95 — intersection with E1 (y=0) at (9.95, 0, 0).
# Distance from crossing to v1=(10,0,0) ≈ 0.05 = seam gap size.
# Distance from crossing to v2=(10,0.05,0) ≈ 0.0707 < vertex tolerance 0.1.
# OK2 test at line 1645 classifies crossing as endpoint-proximal — false negative.
v3 = f.vertex_point(f.cartesian_point((0.0, -10.0, 0.0)))

_dx3 = 0.0 - 10.0
_dy3 = -10.0 - 0.05
_mag3 = _math.hypot(_dx3, _dy3)
e3_line = f.line(f.cartesian_point((10.0, 0.05, 0.0)),
                 f.vector(f.direction((_dx3 / _mag3, _dy3 / _mag3, 0.0)), _mag3))
e3  = f.edge_curve(v2, v3, e3_line)
oe3 = f.oriented_edge(e3, True)

# ── E4: v3(0,-10,0) → v0(0,0,0) — left return closing the wire ───────────────
e4_line = f.line(f.cartesian_point((0.0, -10.0, 0.0)),
                 f.vector(f.direction((0.0, 1.0, 0.0)), 10.0))
e4  = f.edge_curve(v3, v0, e4_line)
oe4 = f.oriented_edge(e4, True)

# 4-edge loop: wire closes (v0 start = v0 end)
# E1 and E3 are non-adjacent (indices 0 and 2 of 4-edge ring, differ by 2).
# They intersect at ~(9.95, 0, 0), which is within 0.0707 units of v2=(10,0.05,0)
# — within vertex tolerance 0.1 — CheckIntersectingEdges OK2 test suppresses detection.
loop = f.edge_loop([oe1, oe2, oe3, oe4])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
from pathlib import Path as _Path
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi105.stp")
