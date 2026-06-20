"""Twi195 — CheckClosed open-tail-vs-spur.

Catalog claim: ShapeAnalysis_Wire.CheckClosed reports wire as unclosed due to a
small trailing spur (gap ~1e-6) but the boolean closed/open classification loses
nuance for "almost closed" wire that could benefit from spur removal vs. closure
repair.

Mechanism: Wire has four edges; first three form a nearly-closed loop with the
endpoint arriving at (0, 1e-6, 0); the fourth edge (spur) goes from that point
back to (0, 0, 0), closing to within 1e-6 of the start. CheckClosed returns
false (unclosed) because the gap exceeds Precision::Confusion, but doesn't
distinguish between a genuine gap and a near-closure spur requiring a different
repair strategy.

Concretely: rectangular wire on a PLANE.
  E0: (0,0,0) → (10,0,0)      [bottom, correct]
  E1: (10,0,0) → (10,10,0)    [right, correct]
  E2: (10,10,0) → (0,1e-6,0)  [top+left diagonal, nearly closes to Y-axis origin]
  E3: (0,1e-6,0) → (0,0,0)    [spur: 1e-6 closing sliver back to origin]

The wire is NOT geometrically closed (CheckClosed returns false) because the
E2→E3 junction has a start vertex at Y=1e-6. The spur E3 is the defect:
it is a 1e-6 length edge that looks like a near-closure, not a genuine gap.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

GAP = 1e-6

f = StepFile(
    catalog_id="Twi195",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; outer EDGE_LOOP has "
        "4 LINE edges; E0-E2 form a near-closed triangle-ish path ending at "
        "(0, 1e-6, 0); E3 is a 1e-6-long spur from (0,1e-6,0) back to (0,0,0); "
        "CheckClosed returns false but cannot distinguish spur vs genuine gap — "
        "open-tail-vs-spur IS the mechanism; EDGE_LOOP IS wired into "
        "FACE_OUTER_BOUND -> ADVANCED_FACE in CLOSED_SHELL — never orphaned"
    ),
)

# ── PLANE: normal +Z, origin at (0,0,0) ─────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices ─────────────────────────────────────────────────────────────────
P0 = (0.0,    0.0,    0.0)
P1 = (10.0,   0.0,    0.0)
P2 = (10.0,   10.0,   0.0)
P3 = (0.0,    GAP,    0.0)   # spur start: 1e-6 above origin

v0 = f.vertex_point(f.cartesian_point(P0))
v1 = f.vertex_point(f.cartesian_point(P1))
v2 = f.vertex_point(f.cartesian_point(P2))
v3 = f.vertex_point(f.cartesian_point(P3))

# ── E0: P0→P1 (bottom) ──────────────────────────────────────────────────────
ln_e0 = f.line(f.cartesian_point(P0), f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
e0 = f.edge_curve(v0, v1, ln_e0)

# ── E1: P1→P2 (right) ───────────────────────────────────────────────────────
ln_e1 = f.line(f.cartesian_point(P1), f.vector(f.direction((0.0, 1.0, 0.0)), 10.0))
e1 = f.edge_curve(v1, v2, ln_e1)

# ── E2: P2→P3 diagonal (top-to-near-origin) — not perfectly closing ─────────
import math as _math
dx2, dy2 = P3[0] - P2[0], P3[1] - P2[1]
mag2 = _math.sqrt(dx2*dx2 + dy2*dy2)
ln_e2 = f.line(
    f.cartesian_point(P2),
    f.vector(f.direction((dx2 / mag2, dy2 / mag2, 0.0)), mag2),
)
e2 = f.edge_curve(v2, v3, ln_e2)

# ── E3: P3→P0 (spur — 1e-6 long, IS the defect) ────────────────────────────
ln_e3 = f.line(
    f.cartesian_point(P3),
    f.vector(f.direction((0.0, -1.0, 0.0)), GAP),
)
e3 = f.edge_curve(v3, v0, ln_e3)

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])
fob   = f.face_outer_bound(loop)
face  = f.advanced_face([fob], plane)
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi195.stp")
