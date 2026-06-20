"""Tfa238 — ShapeFix_Face.SplitEdge (line-2741)

Multi-point edge subdivision; overlapping parameter intervals via meridian
B-spline and closing circle on spherical patch.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a SPHERICAL_SURFACE. The
face has a 3-edge EDGE_LOOP: a B-spline meridian curve from the south pole to
the equator (as the seam), a quarter-circle arc at the equator, and the
closing seam back to the south pole. The B-spline meridian has degree 2 with 3
control points, parametrized from 0 to 1 in a way that causes overlapping
parameter intervals at the split location (line 2741 of ShapeFix_Face). The
SplitEdge routine must subdivide the meridian at the overlap region using
multi-point subdivision; the closing circle provides the reference geometry for
the parameter overlap check.

Byte assertions:
  - contains(b'SPHERICAL_SURFACE')
  - contains(b'B_SPLINE_CURVE_WITH_KNOTS')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa238",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on SPHERICAL_SURFACE radius=2.0; "
        "3-edge EDGE_LOOP: meridian B-spline(T) + equator arc(T) + meridian(F); "
        "B-spline meridian: degree 2, 3 ctrl pts, south-pole→equator seam curve; "
        "closing circle: quarter-arc at equator; "
        "ShapeFix_Face::SplitEdge (line 2741): multi-point edge subdivision; "
        "overlapping parameter intervals at split location on meridian; "
        "split uses closing circle geometry for parameter-overlap check; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

R = 2.0

# ── SPHERICAL_SURFACE ─────────────────────────────────────────────────────────
sph_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
sphere = f.spherical_surface(sph_plc, R)

# ── B-spline meridian from south pole (0,0,-R) to equator point (R,0,0) ──────
# Degree 2, 3 control points: at south pole, mid-point, and equator.
# These create a gentle arc in the XZ-plane simulating a great-circle meridian.
# Overlapping intervals arise because the B-spline approximates the same arc
# that the sphere's native parameterization uses — causing parameter redundancy.
cp0 = f.cartesian_point(( 0.0,  0.0, -R))   # south pole
cp1 = f.cartesian_point(( R,    0.0, -R))   # control point (pulls arc out)
cp2 = f.cartesian_point(( R,    0.0,  0.0)) # equator at x=R

# degree=2, 3 pts → sum(mults)=3+2+1=6 → [3,3] at [0,1]
meridian = f.b_spline_curve_with_knots(
    2,
    [cp0, cp1, cp2],
    [3, 3],
    [0.0, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
)

v_south  = f.vertex_point(cp0)
v_equator = f.vertex_point(cp2)

seam_edge = f.edge_curve(v_south, v_equator, meridian)

# ── Equator arc: quarter circle at z=0 from (R,0,0) to (0,R,0) ──────────────
# Closing circle — the reference geometry for the parameter overlap check.
eq_ctr  = f.cartesian_point((0.0, 0.0, 0.0))
eq_plc  = f.axis2_placement_3d(eq_ctr, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
eq_circ = f.circle(eq_plc, R)

pt_eq2  = f.cartesian_point((0.0, R, 0.0))   # second equator point at (0,R,0)
v_eq2   = f.vertex_point(pt_eq2)
arc_edge = f.edge_curve(v_equator, v_eq2, eq_circ)

# ── Second meridian: B-spline from (0,R,0) back to south pole ────────────────
# Mirrors first meridian in the YZ-plane.
cp3 = f.cartesian_point((0.0, R,   0.0))   # equator at y=R
cp4 = f.cartesian_point((0.0, R,  -R))    # control point
cp5 = f.cartesian_point((0.0, 0.0, -R))   # south pole (same as cp0)

meridian2 = f.b_spline_curve_with_knots(
    2,
    [cp3, cp4, cp5],
    [3, 3],
    [0.0, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
)
close_edge = f.edge_curve(v_eq2, v_south, meridian2)

# ── EDGE_LOOP: seam(T) + arc(T) + close(T) ───────────────────────────────────
face_loop = f.edge_loop([
    f.oriented_edge(seam_edge,  True),
    f.oriented_edge(arc_edge,   True),
    f.oriented_edge(close_edge, True),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], sphere)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa238.stp")
