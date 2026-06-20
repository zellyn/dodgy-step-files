"""Twi267 — ShapeAnalysis_Wire.CheckOuterBound

Catalog claim: Wire outer-bound detection; IsOuterBound flag not propagated
correctly after outer boundary classification.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with four edges
'outer_e1'..'outer_e4' forming a closed rectangular boundary. The wire is
intended to be classified as an outer boundary, but the GEOMETRIC_CURVE_SET
context provides no FACE_OUTER_BOUND wrapper so the IsOuterBound flag is never
set. ShapeAnalysis_Wire::CheckOuterBound relies on the outer-bound flag being
propagated through the wire/face hierarchy; without a FACE_OUTER_BOUND, the
flag is absent and the outer-bound check returns a false-negative IS the
propagation defect. GEOMETRIC_CURVE_SET yields empty on import.

Byte assertions:
  - contains(b'outer_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi267",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with four edges forming closed rectangle; "
        "outer_e1/outer_e2/outer_e3/outer_e4: rectangle (0,0,0)-(2,0,0)-(2,1,0)-(0,1,0)-(0,0,0); "
        "no FACE_OUTER_BOUND wrapper — IsOuterBound flag never set in wire hierarchy; "
        "CheckOuterBound requires flag propagation from FACE_OUTER_BOUND; absence IS propagation defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# Rectangle vertices
vV0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
vV1 = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))
vV2 = f.vertex_point(f.cartesian_point((2.0, 1.0, 0.0)))
vV3 = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0)))

# outer_e1: V0 -> V1
d1  = f.direction((1.0, 0.0, 0.0))
v1  = f.vector(d1, 2.0)
ln1 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v1)
ec1 = f._emit_raw(
    f"EDGE_CURVE('outer_e1',#{vV0.eid},#{vV1.eid},#{ln1.eid},.T.)"
)

# outer_e2: V1 -> V2
d2  = f.direction((0.0, 1.0, 0.0))
v2  = f.vector(d2, 1.0)
ln2 = f.line(f.cartesian_point((2.0, 0.0, 0.0)), v2)
ec2 = f._emit_raw(
    f"EDGE_CURVE('outer_e2',#{vV1.eid},#{vV2.eid},#{ln2.eid},.T.)"
)

# outer_e3: V2 -> V3
d3  = f.direction((-1.0, 0.0, 0.0))
v3  = f.vector(d3, 2.0)
ln3 = f.line(f.cartesian_point((2.0, 1.0, 0.0)), v3)
ec3 = f._emit_raw(
    f"EDGE_CURVE('outer_e3',#{vV2.eid},#{vV3.eid},#{ln3.eid},.T.)"
)

# outer_e4: V3 -> V0
d4  = f.direction((0.0, -1.0, 0.0))
v4  = f.vector(d4, 1.0)
ln4 = f.line(f.cartesian_point((0.0, 1.0, 0.0)), v4)
ec4 = f._emit_raw(
    f"EDGE_CURVE('outer_e4',#{vV3.eid},#{vV0.eid},#{ln4.eid},.T.)"
)

oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec4.eid},.T.)")

# Bare EDGE_LOOP — no FACE_OUTER_BOUND wrapper IS the outer-bound propagation defect
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi267.stp")
