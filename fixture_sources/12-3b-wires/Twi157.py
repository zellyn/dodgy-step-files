"""Twi157 — ShapeAnalysis_Wire.CheckSelfIntersection figure-8 wire.

Catalog claim: Wire whose path forms a figure-8 (crosses itself at exactly one
point). CheckSelfIntersection must detect the crossing at the self-intersection
point where the two lobes of the figure-8 meet.

Mechanism IS a planar ADVANCED_FACE whose outer EDGE_LOOP traces a figure-8:
  - The figure-8 is built from 4 straight line segments forming two triangles
    that share a crossing vertex at (5,5,0):
      E0: LINE (0,0,0) → (10,10,0)   — left-lobe diagonal going up-right
      E1: LINE (10,10,0) → (10,0,0)  — right side
      E2: LINE (10,0,0) → (0,10,0)   — second diagonal going up-left,
                                         crosses E0 at (5,5,0)
      E3: LINE (0,10,0) → (0,0,0)    — left side, closes the loop

The diagonals E0 and E2 cross at (5,5,0): that is the figure-8 crossover.
CheckSelfIntersection must detect that the wire crosses itself, but whether it
correctly identifies and handles the crossing point is implementation-dependent.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi157",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; "
        "outer EDGE_LOOP of 4 LINE edges traces a figure-8 that self-crosses "
        "at (5,5,0): "
        "E0 LINE (0,0,0)→(10,10,0), "
        "E1 LINE (10,10,0)→(10,0,0), "
        "E2 LINE (10,0,0)→(0,10,0) — crosses E0 at (5,5,0) IS the defect, "
        "E3 LINE (0,10,0)→(0,0,0); "
        "CheckSelfIntersection must detect the single crossing at (5,5,0); "
        "figure-8 self-crossing IS the mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND → ADVANCED_FACE in "
        "CLOSED_SHELL — never orphaned"
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
P1 = (10.0, 10.0, 0.0)
P2 = (10.0, 0.0,  0.0)
P3 = (0.0,  10.0, 0.0)

v_P0 = f.vertex_point(f.cartesian_point(P0))
v_P1 = f.vertex_point(f.cartesian_point(P1))
v_P2 = f.vertex_point(f.cartesian_point(P2))
v_P3 = f.vertex_point(f.cartesian_point(P3))


def _line_edge(v_src, v_dst, src, dst):
    dx = dst[0] - src[0]
    dy = dst[1] - src[1]
    dz = dst[2] - src[2]
    mag = _math.sqrt(dx * dx + dy * dy + dz * dz)
    ln = f.line(
        f.cartesian_point(src),
        f.vector(f.direction((dx / mag, dy / mag, dz / mag)), mag),
    )
    return f.edge_curve(v_src, v_dst, ln, True)


# ── E0: (0,0,0) → (10,10,0) — first diagonal ────────────────────────────────
e0  = _line_edge(v_P0, v_P1, P0, P1)
oe0 = f.oriented_edge(e0, True)

# ── E1: (10,10,0) → (10,0,0) — right side ───────────────────────────────────
e1  = _line_edge(v_P1, v_P2, P1, P2)
oe1 = f.oriented_edge(e1, True)

# ── E2: (10,0,0) → (0,10,0) — second diagonal, CROSSES E0 at (5,5,0) ────────
# Verification: E0 param: (0,0)+(10t,10t). E2 param: (10,0)+(-10s,10s).
# Crossing: 10t=10-10s, 10t=10s → 10t=10s → t=s; 10t=10-10t → 20t=10 → t=0.5
# So intersection at t=s=0.5: (5,5,0) — confirmed interior point on both edges.
e2  = _line_edge(v_P2, v_P3, P2, P3)
oe2 = f.oriented_edge(e2, True)

# ── E3: (0,10,0) → (0,0,0) — left side, closes loop ─────────────────────────
e3  = _line_edge(v_P3, v_P0, P3, P0)
oe3 = f.oriented_edge(e3, True)

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f.edge_loop([oe0, oe1, oe2, oe3])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi157.stp")
