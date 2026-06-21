"""Hea017 — Extrude of 2D Offset of Sketch fails STEP export as non-manifold.

Catalog claim (FreeCAD #23694): A Pad whose profile is a 2D Offset of an open
path emits a STEP whose extruded sweep has a discontinuity where the offset
trace self-intersected. The on-disk symptom is a MANIFOLD_SOLID_BREP whose
side-wall contains an ADVANCED_FACE with an EDGE_LOOP whose underlying
B_SPLINE_CURVE_WITH_KNOTS has its first and last control points equal but
with opposite tangents — a degenerate-loop edge.

Mechanism: A CLOSED_SHELL containing one ADVANCED_FACE on a PLANE.
The face's outer EDGE_LOOP has a single ORIENTED_EDGE whose EDGE_CURVE is
a degree-3 B_SPLINE_CURVE_WITH_KNOTS with 4 control points where:
  cp0=(0,0,0), cp1=(1,1,0), cp2=(1,-1,0), cp3=(0,0,0)
The first and last control points are identical (cp0==cp3), and the middle
points double back (cp1 and cp2 are on opposite sides → opposite tangents).
This forms a degenerate loop.

Byte assertions:
  - contains(b'B_SPLINE_CURVE_WITH_KNOTS')
  - contains(b'EDGE_LOOP')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Hea017",
    defect=(
        "MANIFOLD_SOLID_BREP (CLOSED_SHELL) with ONE ADVANCED_FACE on PLANE; "
        "face outer EDGE_LOOP: single degenerate-loop B_SPLINE_CURVE_WITH_KNOTS "
        "(degree 3, cp0=(0,0,0), cp1=(1,1,0), cp2=(1,-1,0), cp3=(0,0,0)); "
        "first==last ctrl pt with opposite tangents (doubles back); "
        "edge start==end vertex (closed degenerate loop); "
        "FreeCAD #23694: self-intersecting 2D offset extrude sweep"
    ),
)

# ── 4 B-spline control points: degenerate loop ────────────────────────────────
# degree 3, 4 ctrl pts → knot sum = 4+3+1=8 → (4,4) at (0.0, 1.0)
cp0 = f.cartesian_point((0.0, 0.0, 0.0), name="cp0")
cp1 = f.cartesian_point((1.0, 1.0, 0.0), name="cp1")
cp2 = f.cartesian_point((1.0, -1.0, 0.0), name="cp2")
cp3 = f.cartesian_point((0.0, 0.0, 0.0), name="cp3")  # same as cp0!

bspline = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[cp0, cp1, cp2, cp3],
    knot_multiplicities=[4, 4],
    knots=[0.0, 1.0],
    name="degenerate_loop",
)

# ── Degenerate edge: start == end vertex ─────────────────────────────────────
v_seam = f.vertex_point(cp0)   # cp0 == cp3
edge   = f._emit_raw(
    f"EDGE_CURVE('',#{v_seam.eid},#{v_seam.eid},#{bspline.eid},.T.)"
)
oe   = f.oriented_edge(edge, True)
loop = f.edge_loop([oe], name="degenerate_edge_loop")

# ── ADVANCED_FACE on PLANE ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="side_wall")

shell = f.closed_shell([face])
solid = f.manifold_solid_brep(shell, name="Hea017_body")

f.add_product_chain(solid, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea017.stp")
