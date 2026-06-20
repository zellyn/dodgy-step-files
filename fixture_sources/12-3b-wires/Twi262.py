"""Twi262 — CheckOrder nullface

Catalog claim: ShapeAnalysis_Wire.CheckOrder silently skips validation when 2D
mode requested but face context is null.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with three connected
edges 'order_e1', 'order_e2', 'order_e3' forming an open chain in 3D with no
face context (no ADVANCED_FACE wrapping). When ShapeAnalysis_Wire::CheckOrder
is invoked with the 2D flag but no face context is set, it silently returns
without performing edge-order validation IS the defect. The bare EDGE_LOOP
without any face wrapper ensures the face context remains null at runtime.

Byte assertions:
  - contains(b'order_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi262",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with three edges, no face context; "
        "order_e1/order_e2/order_e3: open chain edges — no ADVANCED_FACE wrapper IS null-face defect; "
        "CheckOrder in 2D mode requires face context; null face causes silent skip IS validation defect; "
        "bare EDGE_LOOP (no FACE_OUTER_BOUND) ensures face context remains null; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# Three vertices forming an open chain
vV0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
vV1 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
vV2 = f.vertex_point(f.cartesian_point((1.0, 1.0, 0.0)))
vV3 = f.vertex_point(f.cartesian_point((2.0, 1.0, 0.0)))

# order_e1: V0 -> V1
d1  = f.direction((1.0, 0.0, 0.0))
v1  = f.vector(d1, 1.0)
ln1 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v1)
ec1 = f._emit_raw(
    f"EDGE_CURVE('order_e1',#{vV0.eid},#{vV1.eid},#{ln1.eid},.T.)"
)

# order_e2: V1 -> V2
d2  = f.direction((0.0, 1.0, 0.0))
v2  = f.vector(d2, 1.0)
ln2 = f.line(f.cartesian_point((1.0, 0.0, 0.0)), v2)
ec2 = f._emit_raw(
    f"EDGE_CURVE('order_e2',#{vV1.eid},#{vV2.eid},#{ln2.eid},.T.)"
)

# order_e3: V2 -> V3 (open — no face context)
d3  = f.direction((1.0, 0.0, 0.0))
v3  = f.vector(d3, 1.0)
ln3 = f.line(f.cartesian_point((1.0, 1.0, 0.0)), v3)
ec3 = f._emit_raw(
    f"EDGE_CURVE('order_e3',#{vV2.eid},#{vV3.eid},#{ln3.eid},.T.)"
)

oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# Bare EDGE_LOOP — no face wrapper IS the null-face defect
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi262.stp")
