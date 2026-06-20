"""Twi259 — self-loop-binding

Catalog claim: Two self-loop edges at same vertex. Double-append required
(Extent=4). Without: Extent=2, no multi-vertex detection.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with two self-loop
edges 'loop_e1' and 'loop_e2', both having V1==V2==vV0. When
ShapeAnalysis_Wire::CheckLoop builds the vertex-edge map, each self-loop edge
must be appended to vV0's list twice (once for V1, once for V2); without
double-append the extent stays at 2 and the multi-vertex condition
(Extent>=4) is never triggered IS the defect.

Byte assertions:
  - contains(b'loop_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi259",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with two self-loop edges at same vertex; "
        "loop_e1: EDGE_CURVE V0->V0 LINE magnitude=1 IS first self-loop; "
        "loop_e2: EDGE_CURVE V0->V0 LINE magnitude=1 IS second self-loop; "
        "CheckLoop must double-append each self-loop edge to vertex list (Extent=4); "
        "without double-append Extent=2, isMultiVertex not triggered IS detection defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# Single vertex — both edges are self-loops on vV0
vV0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))

# loop_e1: first self-loop IS part of defect condition
d1  = f.direction((1.0, 0.0, 0.0))
v1  = f.vector(d1, 1.0)
ln1 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v1)
ec1 = f._emit_raw(
    f"EDGE_CURVE('loop_e1',#{vV0.eid},#{vV0.eid},#{ln1.eid},.T.)"
)

# loop_e2: second self-loop IS part of defect condition
d2  = f.direction((0.0, 1.0, 0.0))
v2  = f.vector(d2, 1.0)
ln2 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v2)
ec2 = f._emit_raw(
    f"EDGE_CURVE('loop_e2',#{vV0.eid},#{vV0.eid},#{ln2.eid},.T.)"
)

oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi259.stp")
