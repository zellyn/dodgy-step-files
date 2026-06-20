"""Twi257 — unloaded-or-trivial-wire

Catalog claim: Single edge (NbEdges<2); CheckLoop returns false immediately.
Without IsLoaded/NbEdges guard, iteration causes false classification.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with exactly one
'trivial_e' edge (NbEdges==1). When ShapeAnalysis_Wire::CheckLoop is invoked
the NbEdges<2 condition must trigger an early return of false before any
loop-detection iteration; without the IsLoaded/NbEdges guard the iteration
proceeds on a single-edge wire and may falsely classify it as a loop IS the
defect. The single edge connects two distinct vertices so it is not a
degenerate self-loop.

Byte assertions:
  - contains(b'trivial_e')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi257",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with single edge; "
        "trivial_e: EDGE_CURVE V0(0,0,0)->V1(1,0,0) LINE magnitude=1; "
        "NbEdges==1 (<2) IS trivial-wire condition for CheckLoop; "
        "without IsLoaded/NbEdges guard iteration proceeds on single edge IS false-classification defect; "
        "CheckLoop must return false immediately when NbEdges<2; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_LOOP has no wrapping FACE — bare loop"
    ),
)

# Two distinct vertices for the single trivial edge
vV0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
vV1 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))

# trivial_e: single edge with NbEdges==1 IS the defect condition
d_x  = f.direction((1.0, 0.0, 0.0))
vec  = f.vector(d_x, 1.0)
ln   = f.line(f.cartesian_point((0.0, 0.0, 0.0)), vec)
ec_triv = f._emit_raw(
    f"EDGE_CURVE('trivial_e',#{vV0.eid},#{vV1.eid},#{ln.eid},.T.)"
)

oe_triv = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_triv.eid},.T.)")

# Single-edge EDGE_LOOP IS trivial wire (NbEdges<2)
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe_triv.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi257.stp")
