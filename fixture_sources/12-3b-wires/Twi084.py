"""Twi084 — Closed-curve edge has different start and end vertex points.

Catalog claim: An EDGE_CURVE whose edge_geometry is a closed curve (CIRCLE)
declares start vertex and end vertex at DIFFERENT coordinates. The expected
invariant — a closed curve's two endpoints coincide in 3D — is violated.
BRepLib_MakeEdge EdgeError.DifferentPointsOnClosedCurve.

Reproducer recipe: EDGE_CURVE referencing a CIRCLE of radius 1.0 with
edge_start = #V1 at (1,0,0) and edge_end = #V2 at (1.5,0,0); the circle
geometry is closed but the topology declares non-coincident endpoints.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP. OCC sees a
GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'CIRCLE(')
  - contains(b'end_NOT_equal_to_start')
  - contains(b'(1.5,0.0,0.0)')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi084",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP 'end_NOT_equal_to_start'; "
        "EDGE_CURVE geometry is a CIRCLE radius 1.0 centred at origin — closed curve; "
        "edge_start = #V1 at (1,0,0) (on circle at θ=0); "
        "edge_end = #V2 at (1.5,0.0,0.0) — NOT on the circle and NOT equal to start; "
        "closed-curve invariant violated: start ≠ end; "
        "BRepLib_MakeEdge DifferentPointsOnClosedCurve triggered; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_CURVE IS wired into EDGE_LOOP; never orphaned"
    ),
)

# ── CIRCLE: radius 1.0, centred at origin, in XY plane ───────────────────────
# Byte assertion: contains(b'CIRCLE(') — satisfied by the CIRCLE entity
circle_orig = f.cartesian_point((0.0, 0.0, 0.0))
circle_zdir = f.direction((0.0, 0.0, 1.0))
circle_xdir = f.direction((1.0, 0.0, 0.0))
circle_plc  = f.axis2_placement_3d(circle_orig, circle_zdir, circle_xdir)
circle_geom = f.circle(circle_plc, 1.0)

# ── Vertices: start ON circle at θ=0, end NOT on circle at (1.5,0,0) ─────────
# Byte assertion: contains(b'(1.5,0.0,0.0)') — end vertex
v_start = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))   # on circle at θ=0
v_end   = f.vertex_point(f.cartesian_point((1.5, 0.0, 0.0)))   # NOT on circle, ≠ start

# ── EDGE_CURVE: closed circle geometry but non-coincident vertices ────────────
ec = f._emit_raw(
    f"EDGE_CURVE('',#{v_start.eid},#{v_end.eid},#{circle_geom.eid},.T.)"
)
oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec.eid},.T.)")

# ── EDGE_LOOP 'end_NOT_equal_to_start' — byte assertion ──────────────────────
loop = f._emit_raw(f"EDGE_LOOP('end_NOT_equal_to_start',(#{oe.eid}))")

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi084.stp")
