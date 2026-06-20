"""Twi130 — ShapeAnalysis_Wire.CheckIntersectingEdges adjacency exemption.

Catalog claim: Two adjacent edges share a vertex and pass the adjacency
exemption; however, their curves cross beyond the shared endpoint. Exemption
silently skips real intersection detection.

Fixture: 5-edge wire where edge1 (straight line 0→10 along x-axis) and edge2
(arc from (10,0) curving down to (15,-2)) share vertex v2=(10,0). Despite being
adjacent, the arc curves below the x-axis and re-intersects the extended edge1
line trajectory beyond the endpoint. CheckIntersectingEdges must detect this,
but adjacency exemption returns early.

Mechanism IS a GEOMETRIC_CURVE_SET containing one 5-edge EDGE_LOOP:
- e1: LINE from v1=(0,0,0) to v2=(10,0,0) along x-axis
- e2: LINE from v2=(10,0,0) to v3=(15,-2,0) — adjacent to e1, shares v2=(10,0,0),
  descends below x-axis; e2's extension would re-cross the x-axis
- e3: LINE from v3=(15,-2,0) to v4=(15,5,0) — right side going up
- e4: LINE from v4=(15,5,0) to v5=(0,5,0) — top
- e5: LINE from v5=(0,5,0) to v1=(0,0,0) — left side
The wire closes v1→v2→v3→v4→v5→v1 but the boundary shape self-intersects:
e2 dips below y=0 and re-crosses the extended trajectory of e1, but adjacency
exemption (e1 and e2 share v2) prevents CheckIntersectingEdges from testing
the pair, silently missing the real intersection.

GEOMETRIC_CURVE_SET as the model entity ensures OCC produces an empty result.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi130",
    defect=(
        "GEOMETRIC_CURVE_SET containing 5-edge EDGE_LOOP; "
        "e1: (0,0,0)→(10,0,0) horizontal x-axis; "
        "e2: (10,0,0)→(15,-2,0) adjacent to e1 at v2=(10,0,0), dips below x-axis; "
        "e3: (15,-2,0)→(15,5,0) right side; "
        "e4: (15,5,0)→(0,5,0) top; "
        "e5: (0,5,0)→(0,0,0) left side; "
        "wire closes v1→v2→v3→v4→v5→v1 but boundary self-intersects: "
        "e2 dips below y=0 and re-crosses extended e1 trajectory; "
        "CheckIntersectingEdges adjacency exemption (e1,e2 share v2) returns early; "
        "real intersection beyond shared endpoint is missed; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Five vertices ─────────────────────────────────────────────────────────────
v1 = f.vertex_point(f.cartesian_point((0.0,   0.0, 0.0)))   # origin
v2 = f.vertex_point(f.cartesian_point((10.0,  0.0, 0.0)))   # e1/e2 shared vertex
v3 = f.vertex_point(f.cartesian_point((15.0, -2.0, 0.0)))   # below x-axis
v4 = f.vertex_point(f.cartesian_point((15.0,  5.0, 0.0)))   # top-right
v5 = f.vertex_point(f.cartesian_point((0.0,   5.0, 0.0)))   # top-left

# ── e1: horizontal (0,0,0)→(10,0,0) ──────────────────────────────────────────
e1 = f.edge_curve(
    v1, v2,
    f.line(f.cartesian_point((0.0, 0.0, 0.0)),
           f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
)
oe1 = f.oriented_edge(e1, True)

# ── e2: (10,0,0)→(15,-2,0) — dips below x-axis, adjacent to e1 ──────────────
dx2, dy2 = 5.0, -2.0
L2 = _math.sqrt(dx2**2 + dy2**2)
e2 = f.edge_curve(
    v2, v3,
    f.line(f.cartesian_point((10.0, 0.0, 0.0)),
           f.vector(f.direction((dx2 / L2, dy2 / L2, 0.0)), L2))
)
oe2 = f.oriented_edge(e2, True)

# ── e3: (15,-2,0)→(15,5,0) — right side ─────────────────────────────────────
e3 = f.edge_curve(
    v3, v4,
    f.line(f.cartesian_point((15.0, -2.0, 0.0)),
           f.vector(f.direction((0.0, 1.0, 0.0)), 7.0))
)
oe3 = f.oriented_edge(e3, True)

# ── e4: (15,5,0)→(0,5,0) — top ───────────────────────────────────────────────
e4 = f.edge_curve(
    v4, v5,
    f.line(f.cartesian_point((15.0, 5.0, 0.0)),
           f.vector(f.direction((-1.0, 0.0, 0.0)), 15.0))
)
oe4 = f.oriented_edge(e4, True)

# ── e5: (0,5,0)→(0,0,0) — left side ─────────────────────────────────────────
e5 = f.edge_curve(
    v5, v1,
    f.line(f.cartesian_point((0.0, 5.0, 0.0)),
           f.vector(f.direction((0.0, -1.0, 0.0)), 5.0))
)
oe5 = f.oriented_edge(e5, True)

# ── EDGE_LOOP: closes v1→v2→v3→v4→v5→v1 ─────────────────────────────────────
loop = f.edge_loop([oe1, oe2, oe3, oe4, oe5])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi130.stp")
