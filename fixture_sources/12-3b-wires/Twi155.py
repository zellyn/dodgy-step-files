"""Twi155 — ShapeAnalysis_Wire.CheckGap3d zero-length-edge.

Catalog claim: Wire contains a zero-length edge (start vertex == end vertex at
the same point). CheckGap3d's adjacent-edge gap check at line 1125 computes the
distance between edge[i] end and edge[i+1] start. When edge[i] is zero-length
(start == end at the same point), it has no well-defined direction, and the
floating-point evaluation order of the gap computation becomes non-deterministic.

Mechanism IS a planar ADVANCED_FACE whose outer EDGE_LOOP contains 4 edges:
  - E0: LINE (0,0,0) → (10,0,0)      — normal bottom edge
  - E1: zero-length LINE at (10,0,0) → (10,0,0)   — DEFECT: degenerate edge
        with a LINE curve of magnitude 0.0
  - E2: LINE (10,0,0) → (10,10,0)    — normal right edge
  - E3: LINE (10,10,0) → (0,0,0)     — closes the triangle

The zero-length LINE (magnitude 0) has both vertices at (10,0,0); it is a
genuine degenerate edge. CheckGap3d at line 1125 does not guard against
start==end; when processing the gap between E1's end and E2's start, the
distance is 0 but the direction is undefined — floating-point order determines
whether this registers as a gap or not.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi155",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; "
        "outer EDGE_LOOP has 4 edges: "
        "E0 LINE (0,0,0)→(10,0,0), "
        "E1 zero-length LINE (10,0,0)→(10,0,0) magnitude=0 IS the defect, "
        "E2 LINE (10,0,0)→(10,10,0), "
        "E3 LINE (10,10,0)→(0,0,0); "
        "E1 start==end vertex at (10,0,0); "
        "CheckGap3d at line 1125 does not guard start==end; "
        "direction undefined at zero-length edge IS the mechanism; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → "
        "ADVANCED_FACE in CLOSED_SHELL — never orphaned"
    ),
)

# ── Plane: normal +Z ──────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices ──────────────────────────────────────────────────────────────────
P0 = (0.0,  0.0,  0.0)
P1 = (10.0, 0.0,  0.0)   # also start==end of zero-length E1
P2 = (10.0, 10.0, 0.0)
# Triangle: P0 → P1 → (zero-length at P1) → P1 → P2 → P0

v_P0 = f.vertex_point(f.cartesian_point(P0))
v_P1 = f.vertex_point(f.cartesian_point(P1))   # shared: E0 end, E1 start, E1 end, E2 start
v_P2 = f.vertex_point(f.cartesian_point(P2))

# ── E0: LINE (0,0,0) → (10,0,0) ──────────────────────────────────────────────
e0_line = f.line(
    f.cartesian_point(P0),
    f.vector(f.direction((1.0, 0.0, 0.0)), 10.0),
)
e0  = f.edge_curve(v_P0, v_P1, e0_line, True)
oe0 = f.oriented_edge(e0, True)

# ── E1: ZERO-LENGTH LINE at (10,0,0) — IS the defect ─────────────────────────
# Magnitude 0.0; direction is nominally +X but irrelevant at zero length.
e1_line = f.line(
    f.cartesian_point(P1),
    f.vector(f.direction((1.0, 0.0, 0.0)), 0.0),   # magnitude == 0
)
e1  = f.edge_curve(v_P1, v_P1, e1_line, True)      # start == end vertex
oe1 = f.oriented_edge(e1, True)

# ── E2: LINE (10,0,0) → (10,10,0) ────────────────────────────────────────────
e2_line = f.line(
    f.cartesian_point(P1),
    f.vector(f.direction((0.0, 1.0, 0.0)), 10.0),
)
e2  = f.edge_curve(v_P1, v_P2, e2_line, True)
oe2 = f.oriented_edge(e2, True)

# ── E3: LINE (10,10,0) → (0,0,0) — closes the wire ──────────────────────────
import math as _math
dx, dy = P0[0] - P2[0], P0[1] - P2[1]
mag = _math.sqrt(dx * dx + dy * dy)
e3_line = f.line(
    f.cartesian_point(P2),
    f.vector(f.direction((dx / mag, dy / mag, 0.0)), mag),
)
e3  = f.edge_curve(v_P2, v_P0, e3_line, True)
oe3 = f.oriented_edge(e3, True)

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f.edge_loop([oe0, oe1, oe2, oe3])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi155.stp")
