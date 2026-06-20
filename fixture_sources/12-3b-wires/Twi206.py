"""Twi206 — ShapeFix_Wire.FixSelfIntersectingEdge cusp-at-vertex.

Catalog claim: Single edge with cusp at start vertex. FixSelfIntersectingEdge
tries to split at cusp but cusp coincides with endpoint, preventing proper
healing.

Mechanism: A 3-edge EDGE_LOOP on a PLANE. One edge (E1) is a cubic B-spline
that has a cusp at its START vertex — the first-derivative vector goes to zero
there (the first two control points are identical), creating a point where the
curve direction reverses. This is the "cusp at vertex" condition: the cusp IS
at the edge endpoint, so FixSelfIntersectingEdge cannot split at the cusp
location (it would split the edge to a zero-length piece at the endpoint).
The inability to split IS the mechanism.

Wire on PLANE (normal +Z):
  P0 = (0, 0, 0)   P1 = (8, 0, 0)   P2 = (4, 6, 0)
  E0: LINE from P0 to P1 (base)
  E1: cubic B-spline from P1 to P2 with cusp at P1 (start vertex).
      Control pts: (8,0,0), (8,0,0), (6,5,0), (4,6,0)
      First two CPs identical => zero first derivative at t=0 => cusp IS at start.
  E2: LINE from P2 to P0 (closing)

The cusp at the start vertex of E1 IS the defect that confounds
FixSelfIntersectingEdge — it detects the cusp but cannot split there because
the cusp coincides with the endpoint.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile
import math as _math

f = StepFile(
    catalog_id="Twi206",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; 3-edge EDGE_LOOP; "
        "E1 is a cubic B_SPLINE_CURVE_WITH_KNOTS from P1=(8,0,0) to P2=(4,6,0) "
        "with first two control points identical at (8,0,0) — zero first derivative "
        "at t=0 creates cusp at start vertex IS the defect; "
        "FixSelfIntersectingEdge detects cusp but cannot split at endpoint — "
        "prevents proper healing IS the mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND -> ADVANCED_FACE in "
        "CLOSED_SHELL — never orphaned"
    ),
)

# -- PLANE: normal +Z ---------------------------------------------------------
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# -- Vertices -----------------------------------------------------------------
P0 = (0.0, 0.0, 0.0)
P1 = (8.0, 0.0, 0.0)
P2 = (4.0, 6.0, 0.0)

v0 = f.vertex_point(f.cartesian_point(P0))
v1 = f.vertex_point(f.cartesian_point(P1))
v2 = f.vertex_point(f.cartesian_point(P2))

# -- E0: P0 -> P1, base LINE --------------------------------------------------
ln_e0 = f.line(f.cartesian_point(P0), f.vector(f.direction((1.0, 0.0, 0.0)), 8.0))
e0 = f.edge_curve(v0, v1, ln_e0)

# -- E1: P1 -> P2, B-spline with cusp at start vertex P1 ---------------------
# Cusp condition: first two control points are identical => C'(0) = 0.
# Control pts: (8,0,0), (8,0,0), (6,5,0), (4,6,0)
# degree=3, 4 control points: sum(mults) = 4+3+1=8; clamped: [4,4]
cp1_pts = [
    f.cartesian_point((8.0, 0.0, 0.0)),   # CP0 — same as CP1 => cusp at t=0
    f.cartesian_point((8.0, 0.0, 0.0)),   # CP1 — identical to CP0
    f.cartesian_point((6.0, 5.0, 0.0)),   # CP2
    f.cartesian_point((4.0, 6.0, 0.0)),   # CP3 = P2
]
bsp_e1 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=cp1_pts,
    knot_multiplicities=[4, 4],
    knots=[0.0, 1.0],
)
e1 = f.edge_curve(v1, v2, bsp_e1)

# -- E2: P2 -> P0, closing LINE -----------------------------------------------
dx2 = P0[0] - P2[0]
dy2 = P0[1] - P2[1]
mag2 = _math.sqrt(dx2*dx2 + dy2*dy2)
ln_e2 = f.line(
    f.cartesian_point(P2),
    f.vector(f.direction((dx2/mag2, dy2/mag2, 0.0)), mag2),
)
e2 = f.edge_curve(v2, v0, ln_e2)

# -- EDGE_LOOP ----------------------------------------------------------------
loop  = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
])
fob   = f.face_outer_bound(loop)
face  = f.advanced_face([fob], plane)
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi206.stp")
