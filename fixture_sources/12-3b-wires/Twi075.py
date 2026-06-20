"""Twi075 — Connect-shape diagnostic: foreign ORIENTED_EDGE attaches to EDGE_LOOP wire.

Catalog claim: An open 3-edge wire and a foreign single edge whose endpoints
could plausibly attach in any of four orientations (foreign-follows-wire-direct,
foreign-follows-wire-reversed, foreign-precedes-wire-direct,
foreign-precedes-wire-reversed) with different residual sub-mm gaps.
ShapeAnalysis_Wire::CheckShapeConnect enumerates all four and reports distances.

Reproducer recipe: An open three-edge wire running (0,0,0)→(1,0,0)→(2,0,0)→(3,0,0)
and a separate single edge ('foreign_edge') between (3.001,0.0,0.0) and (4.0,0.0,0.0)
— wire tail is at (3,0,0), foreign edge start is 0.001 away (sub-mm gap), so
foreign-follows-wire-direct is the closest connection mode.

Mechanism IS a GEOMETRIC_CURVE_SET containing both the EDGE_LOOP 'open_three_edge_wire'
and the foreign EDGE_CURVE. OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'(3.001,0.0,0.0)')
  - contains(b'foreign_edge')
  - contains(b'open_three_edge_wire')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi075",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP 'open_three_edge_wire' (3 edges, open) "
        "and a foreign EDGE_CURVE 'foreign_edge'; "
        "wire runs (0,0,0)→(1,0,0)→(2,0,0)→(3,0,0) — open, not closed; "
        "foreign_edge: (3.001,0.0,0.0)→(4.0,0.0,0.0) — sub-mm gap of 0.001 at wire tail; "
        "CheckShapeConnect enumerates 4 orientations (follows/precedes × direct/reversed) "
        "and reports smallest gap distance; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into structures in GEOMETRIC_CURVE_SET; never orphaned"
    ),
)

# ── Three-edge open wire: (0,0,0)→(1,0,0)→(2,0,0)→(3,0,0) ──────────────────
v0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))   # wire head
v1 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
v2 = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))
v3 = f.vertex_point(f.cartesian_point((3.0, 0.0, 0.0)))   # wire tail

e1 = f.edge_curve(
    v0, v1,
    f.line(f.cartesian_point((0.0, 0.0, 0.0)),
           f.vector(f.direction((1.0, 0.0, 0.0)), 1.0))
)
e2 = f.edge_curve(
    v1, v2,
    f.line(f.cartesian_point((1.0, 0.0, 0.0)),
           f.vector(f.direction((1.0, 0.0, 0.0)), 1.0))
)
e3 = f.edge_curve(
    v2, v3,
    f.line(f.cartesian_point((2.0, 0.0, 0.0)),
           f.vector(f.direction((1.0, 0.0, 0.0)), 1.0))
)

oe1 = f.oriented_edge(e1, True)
oe2 = f.oriented_edge(e2, True)
oe3 = f.oriented_edge(e3, True)

# EDGE_LOOP named 'open_three_edge_wire' — satisfies byte assertion.
# Three edges form an open wire (endpoints do NOT coincide).
loop = f._emit_raw(
    f"EDGE_LOOP('open_three_edge_wire',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# ── Foreign edge: (3.001,0.0,0.0)→(4.0,0.0,0.0) — sub-mm gap at wire tail ──
# Byte assertion: contains(b'(3.001,0.0,0.0)')
vf_start = f.vertex_point(f.cartesian_point((3.001, 0.0, 0.0)))   # byte assertion
vf_end   = f.vertex_point(f.cartesian_point((4.0,   0.0, 0.0)))

foreign_line = f.line(
    f.cartesian_point((3.001, 0.0, 0.0)),
    f.vector(f.direction((1.0, 0.0, 0.0)), 0.999)
)
# Byte assertion: contains(b'foreign_edge') — use name on EDGE_CURVE
foreign_ec = f._emit_raw(
    f"EDGE_CURVE('foreign_edge',#{vf_start.eid},#{vf_end.eid},#{foreign_line.eid},.T.)"
)

# GEOMETRIC_CURVE_SET contains both the open wire loop and the foreign edge.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid},#{foreign_ec.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi075.stp")
