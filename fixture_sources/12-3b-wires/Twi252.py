"""Twi252 — ShapeAnalysis_Wire.CheckConnected.WIRE_NOT_LOADED

Catalog claim: Wire with zero edges; validates that CheckConnected detects
unloaded state. Without IsLoaded guard, null-dereference on edge sequence
access.

Mechanism: GEOMETRIC_CURVE_SET containing a bare EDGE_LOOP with an empty
edge list. When ShapeAnalysis_Wire::CheckConnected is invoked on this wire
the NbEdges() == 0 condition means the wire is not loaded; the IsLoaded
guard must fire before any edge-sequence access. Without the guard a
null-dereference on the edge sequence iterator IS the defect.

Byte assertions:
  - contains(b'zero_edge_loop')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi252",
    defect=(
        "GEOMETRIC_CURVE_SET containing bare EDGE_LOOP with zero edges; "
        "EDGE_LOOP named zero_edge_loop has empty edge list IS unloaded-wire defect; "
        "CheckConnected must detect NbEdges()==0 before any edge-sequence access; "
        "without IsLoaded guard null-dereference on edge iterator IS defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_LOOP has no wrapping FACE — no ADVANCED_FACE present"
    ),
)

# Bare EDGE_LOOP with empty edge list — zero edges IS the defect
loop = f._emit_raw("EDGE_LOOP('zero_edge_loop',())")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi252.stp")
