"""Twi260 — multi-vertex-self-loop-check

Catalog claim: Three self-loop edges at vertex (Extent=6 after append).
Extent>2 and isMultiVertex must add vertex to loop map.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with three self-loop
edges 'loop_e1', 'loop_e2', 'loop_e3', all having V1==V2==vV0. After
double-append, the extent at vV0 reaches 6 (2 per self-loop x 3 edges).
ShapeAnalysis_Wire::CheckLoop must check isMultiVertex when extent>2 and add
vV0 to the loop vertex map; without the extent>2 threshold check, the
multi-vertex state is not detected and the loop classification fails IS the
defect.

Byte assertions:
  - contains(b'loop_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi260",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with three self-loop edges at same vertex; "
        "loop_e1/loop_e2/loop_e3: each EDGE_CURVE V0->V0, double-append yields Extent=6; "
        "CheckLoop must check Extent>2 and call isMultiVertex to add vV0 to loop map; "
        "without Extent>2 threshold, multi-vertex not detected IS false-negative defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# Single vertex — all three edges are self-loops on vV0
vV0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))

# loop_e1
d1  = f.direction((1.0, 0.0, 0.0))
v1  = f.vector(d1, 1.0)
ln1 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v1)
ec1 = f._emit_raw(
    f"EDGE_CURVE('loop_e1',#{vV0.eid},#{vV0.eid},#{ln1.eid},.T.)"
)

# loop_e2
d2  = f.direction((0.0, 1.0, 0.0))
v2  = f.vector(d2, 1.0)
ln2 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v2)
ec2 = f._emit_raw(
    f"EDGE_CURVE('loop_e2',#{vV0.eid},#{vV0.eid},#{ln2.eid},.T.)"
)

# loop_e3
d3  = f.direction((0.0, 0.0, 1.0))
v3  = f.vector(d3, 1.0)
ln3 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v3)
ec3 = f._emit_raw(
    f"EDGE_CURVE('loop_e3',#{vV0.eid},#{vV0.eid},#{ln3.eid},.T.)"
)

oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi260.stp")
