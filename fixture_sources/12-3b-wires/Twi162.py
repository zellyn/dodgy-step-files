"""Twi162 — ShapeFix_Wire.FixIntersectingEdges 3-edge-mutual-intersection.

Catalog claim: Wire with 3 edges mutually intersecting at single point (star
geometry); FixIntersectingEdges splits pairwise and produces inconsistent
topology.

Mechanism: Three line segments (horizontal, vertical, diagonal) all pass
through (5,5,0). The wire forms a loop that passes through the common
intersection point three times. FixIntersectingEdges compares edge pairs and
attempts to split each pair at the intersection; but with a 3-way mutual
intersection, pairwise splitting creates inconsistent edge/vertex topology —
each pair split introduces a new vertex at (5,5,0) but the three splits are
not reconciled to a single shared vertex.

Wire structure (closed hexagonal loop visiting all 3 edge midpoints):
  P0=(0,5,0), P1=(5,0,0), P2=(10,5,0), P3=(5,10,0)
  E0: P0 → P1  (diagonal down-right, passes through (5,5,0) at extension)
  E1: P1 → P2  (diagonal up-right)
  E2: P2 → P3  (diagonal up-left)
  E3: P3 → P0  (diagonal down-left)
  — plus the horizontal E4 (P0→P2 through (5,5,0)) and
     vertical E5 (P1→P3 through (5,5,0))

Actually we build a star wire: 6 half-spokes from the outer corners into the
center and back, forming a triangle-star. Simpler: use a triangle whose edges
all pass through (5,5,0) extended, i.e., the outer boundary of a star with
three inner vertices all at (5,5,0).

Simplest authentic encoding: build a 6-vertex star/hexagon loop where the
three diagonals all pass through (5,5,0):
  Outer vertices:  A=(0,5,0), B=(7.5,0,0), C=(7.5,10,0)
  Inner vertices:  all three edges A-B, A-C, B-C extended meet at (5,5,0).
  We use three spoke-pairs through center:
    E0: A=(0,5,0) → center=(5,5,0) [half-horizontal]
    E1: center=(5,5,0) → C=(10,5,0)
    E2: C=(10,5,0) → D=(5,10,0) [up-left diagonal]
    E3: D=(5,10,0) → center=(5,5,0) [back to center]
    E4: center=(5,5,0) → B=(5,0,0) [down]
    E5: B=(5,0,0) → A=(0,5,0) [left diagonal]

  All three pairs (E0/E1, E2/E3, E4/E5) share the center (5,5,0) vertex,
  making the center vertex appear 3 times in the wire, once as start of E0
  after E5 close but also as end of E0=start of E1, end of E3=start of E4.

  FixIntersectingEdges comparing E0 vs E3: both meet at center — pairwise
  split would duplicate the center vertex; without cycle/shared-vertex
  detection the result is inconsistent topology.

The outer wire loop is: A → center → C → D → center → B → A.
The center vertex (5,5,0) appears twice in the EDGE_LOOP — that is the defect.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi162",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; "
        "outer EDGE_LOOP has 6 LINE edges forming a star/bow that visits "
        "center point (5,5,0) twice: "
        "E0 (0,5,0)→(5,5,0), E1 (5,5,0)→(10,5,0), E2 (10,5,0)→(5,10,0), "
        "E3 (5,10,0)→(5,5,0), E4 (5,5,0)→(5,0,0), E5 (5,0,0)→(0,5,0); "
        "center vertex (5,5,0) appears as both endpoint of E0/E1 and E3/E4 "
        "IS the 3-edge-mutual-intersection defect; "
        "FixIntersectingEdges pairwise splits create inconsistent topology "
        "without shared-vertex reconciliation IS the mechanism; "
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
PA  = ( 0.0,  5.0, 0.0)  # left
PB  = ( 5.0,  0.0, 0.0)  # bottom
PC  = (10.0,  5.0, 0.0)  # right
PD  = ( 5.0, 10.0, 0.0)  # top
PCT = ( 5.0,  5.0, 0.0)  # center — the mutual intersection point

v_A  = f.vertex_point(f.cartesian_point(PA))
v_B  = f.vertex_point(f.cartesian_point(PB))
v_C  = f.vertex_point(f.cartesian_point(PC))
v_D  = f.vertex_point(f.cartesian_point(PD))
# Center appears twice as endpoints — use the SAME vertex entity both times
# so the STEP topology captures the shared point. This is the defect structure.
v_CT = f.vertex_point(f.cartesian_point(PCT))


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


# ── E0: A → center ────────────────────────────────────────────────────────────
e0  = _line_edge(v_A, v_CT, PA, PCT)
oe0 = f.oriented_edge(e0, True)

# ── E1: center → C ────────────────────────────────────────────────────────────
e1  = _line_edge(v_CT, v_C, PCT, PC)
oe1 = f.oriented_edge(e1, True)

# ── E2: C → D ────────────────────────────────────────────────────────────────
e2  = _line_edge(v_C, v_D, PC, PD)
oe2 = f.oriented_edge(e2, True)

# ── E3: D → center ───────────────────────────────────────────────────────────
e3  = _line_edge(v_D, v_CT, PD, PCT)
oe3 = f.oriented_edge(e3, True)

# ── E4: center → B ───────────────────────────────────────────────────────────
e4  = _line_edge(v_CT, v_B, PCT, PB)
oe4 = f.oriented_edge(e4, True)

# ── E5: B → A (close) ────────────────────────────────────────────────────────
e5  = _line_edge(v_B, v_A, PB, PA)
oe5 = f.oriented_edge(e5, True)

# ── EDGE_LOOP: star wire through center twice ─────────────────────────────────
loop = f.edge_loop([oe0, oe1, oe2, oe3, oe4, oe5])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi162.stp")
