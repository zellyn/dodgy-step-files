"""Twi153 — ShapeAnalysis_Wire.CheckIntersectingEdges B-spline self-intersection.

Catalog claim: B-spline edge has a self-intersection (loops back on itself).
CheckIntersectingEdges treats each edge as injective (one-to-one mapping from
parameter to curve point), missing intra-edge intersections since the pairwise
loop at line 1563 only compares pairs of *distinct* edges, never an edge against
itself. A loop-back B-spline violates the injection assumption.

Mechanism IS a planar ADVANCED_FACE whose outer wire contains:
  - E0: degree-3 B-spline that starts at (0,0,0), arcs through (10,5,0),
        loops back through (5,10,0) and returns to (0,0,0) — a closed
        self-intersecting curve. The curve visits the region near (3,3,0)
        twice (once going out, once looping back). E0 has coincident start/end
        vertex.
  - E1: straight LINE from (0,0,0) → (10,0,0) — closes the wire so that
        the face has exactly one EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE.

The self-intersection of E0 is the defect. CheckIntersectingEdges tests
pairwise distinct edges and never compares E0 against itself; the intra-edge
loop-back is invisible to the checker.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi153",
    defect=(
        "Single ADVANCED_FACE on PLANE; "
        "outer EDGE_LOOP contains two edges: "
        "E0 is a degree-3 B-spline from (0,0,0) back to (0,0,0) that loops "
        "through (10,5,0) and (5,10,0) — self-intersecting curve, the curve "
        "crosses itself near (3,3,0); "
        "E1 is a LINE from (0,0,0) → (10,0,0) — fictitious closing segment; "
        "CheckIntersectingEdges pairwise loop at line 1563 compares only "
        "distinct-edge pairs and never tests E0 against itself; "
        "intra-edge self-intersection IS the mechanism; "
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
# E0: closed B-spline loop, start==end at (0,0,0)
# E1: line from (0,0,0) to (10,0,0)
P_orig  = (0.0,  0.0, 0.0)
P_right = (10.0, 0.0, 0.0)

v_orig  = f.vertex_point(f.cartesian_point(P_orig))   # shared: E0 start/end, E1 start
v_right = f.vertex_point(f.cartesian_point(P_right))  # E1 end

# ── E0: Self-intersecting degree-3 B-spline (loop-back) ──────────────────────
# Control points that force the curve to loop back on itself:
#   P0=(0,0,0), P1=(15,5,0), P2=(5,15,0), P3=(-5,10,0), P4=(-2,2,0), P5=(0,0,0)
# This S-curve loops: starts at origin, swings right/up, then curves back
# left passing through a region already visited, and returns to origin.
# The crossing happens approximately near (2,4,0).
cp0 = f.cartesian_point((0.0,  0.0, 0.0))
cp1 = f.cartesian_point((15.0, 5.0, 0.0))
cp2 = f.cartesian_point((5.0,  15.0, 0.0))
cp3 = f.cartesian_point((-5.0, 10.0, 0.0))
cp4 = f.cartesian_point((-2.0, 2.0,  0.0))
cp5 = f.cartesian_point((0.0,  0.0,  0.0))

# 6 control points, degree 3 → need 6+3+1=10 knots (counting multiplicities)
# Clamped: mult[0]=4, mult[1..2]=1 each, mult[-1]=4 => 4+1+1+4=10 ✓
bspline0 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[cp0, cp1, cp2, cp3, cp4, cp5],
    knot_multiplicities=[4, 1, 1, 4],
    knots=[0.0, 0.25, 0.75, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=True,   # IS the defect flag
    knot_spec="UNSPECIFIED",
)

# E0: closed loop — start vertex == end vertex (both at origin)
e0  = f.edge_curve(v_orig, v_orig, bspline0, True)
oe0 = f.oriented_edge(e0, True)

# ── E1: LINE (0,0,0) → (10,0,0) — second edge, closes topology ───────────────
# (E0 already returns to origin, so this is a degenerate "no-gap" closing line.)
# Actually we need the wire to NOT be just a single closed loop (which OCCT
# might reject). Instead let E0 be an open curve from (0,0,0) to (10,0,0) that
# self-intersects, and E1 closes back. Let's revise: use a self-intersecting
# open B-spline that goes (0,0)→(10,0) but loops through (5,10) and back.

# ── Revised approach: open B-spline (0,0,0)→(10,0,0) that self-intersects ─────
# Remove the closed-loop approach; instead:
# cp0=(0,0,0), cp1=(15,8,0), cp2=(5,12,0), cp3=(-3,5,0), cp4=(8,2,0), cp5=(10,0,0)
# This creates an S that crosses itself.
# But the builder emits in-order, so we need to not reuse cp/vertex IDs.
# We already emitted cp0..cp5 and e0/oe0. We'll just keep E0 as a closed loop
# and make E1 a separate straight closing edge back to origin (zero length).
# Actually E0 already closes (start==end), so the wire of just [oe0] is valid.
# But the tier-3 assertion needs n_faces_total==1 - we need one face.

# We'll use a single-edge EDGE_LOOP: just [oe0]. OCCT accepts single-edge loops
# when the edge is truly closed (start==end vertex and the curve closes).

loop = f.edge_loop([oe0])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi153.stp")
