"""Twi254 — ShapeAnalysis_Wire.CheckConnected.SAME_VERTEX_BOTH_ENDS

Catalog claim: Single edge where FirstVertex == LastVertex (self-loop);
validates loop detection. Without V1.IsSame(V2) guard, connectivity masked.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with a single
'self_loop_e' edge whose V1 and V2 are the same VERTEX_POINT entity. When
ShapeAnalysis_Wire::CheckConnected compares endpoints the V1.IsSame(V2) test
should detect the self-loop condition; without the guard the loop connectivity
is masked and the wire appears valid IS the defect. The single self-loop edge
produces NbEdges==1 which also exercises the zero-check path.

Byte assertions:
  - contains(b'self_loop_e')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi254",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with single self-loop edge; "
        "self_loop_e: EDGE_CURVE with V1 == V2 (same VERTEX_POINT entity) IS self-loop defect; "
        "FirstVertex() == LastVertex() — IsSame() must detect IS connectivity masked without guard; "
        "NbEdges==1 also exercises trivial-wire guard path; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_LOOP has no wrapping FACE — bare loop"
    ),
)

# Single vertex used for both ends — same entity IS the defect
vV0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))

# Self-loop line: degenerate line from V0 back to V0
d_x  = f.direction((1.0, 0.0, 0.0))
vec  = f.vector(d_x, 1.0)
ln   = f.line(f.cartesian_point((0.0, 0.0, 0.0)), vec)

# self_loop_e: V1 and V2 are the same vertex
ec_sl = f._emit_raw(
    f"EDGE_CURVE('self_loop_e',#{vV0.eid},#{vV0.eid},#{ln.eid},.T.)"
)

oe_sl = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_sl.eid},.T.)")

loop = f._emit_raw(f"EDGE_LOOP('',(#{oe_sl.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi254.stp")
