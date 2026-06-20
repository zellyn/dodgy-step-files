"""Twi276 — CheckLoop Multi-Vertex V2-Check

Catalog claim: Edges E1(V0->V2), E2(V1->V2), E3(V2->V3). V2 extent=3.
Tests end-vertex (V2) loop detection symmetry.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with three edges
'v2check_e1' (V0->V2), 'v2check_e2' (V1->V2), 'v2check_e3' (V2->V3). Vertex
V2 appears as an endpoint in all three edges (end of e1, end of e2, start of
e3), giving it an extent of 3 in the vertex occurrence count. The CheckLoop
algorithm tests both start vertices (V1) and end vertices (V2) for multi-vertex
loop detection; an asymmetry in the check — where only start-vertex extent is
tested — would miss V2's extent=3. GEOMETRIC_CURVE_SET yields empty on import.

Byte assertions:
  - contains(b'v2check_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi276",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with three edges; V2 appears as endpoint in all three; "
        "v2check_e1: (0,0,0)->(2,0,0) V0->V2; "
        "v2check_e2: (1,0,0)->(2,0,0) V1->V2; "
        "v2check_e3: (2,0,0)->(3,0,0) V2->V3; "
        "V2 extent=3 (end of e1, end of e2, start of e3); "
        "CheckLoop must check end-vertex (V2) extent symmetrically with start-vertex IS detection asymmetry defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# Four vertices: V0, V1, V2, V3
vV0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
vV1 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
vV2 = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))
vV3 = f.vertex_point(f.cartesian_point((3.0, 0.0, 0.0)))

# v2check_e1: V0 -> V2
d1  = f.direction((1.0, 0.0, 0.0))
v1  = f.vector(d1, 2.0)
ln1 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v1)
ec1 = f._emit_raw(
    f"EDGE_CURVE('v2check_e1',#{vV0.eid},#{vV2.eid},#{ln1.eid},.T.)"
)

# v2check_e2: V1 -> V2
d2  = f.direction((1.0, 0.0, 0.0))
v2  = f.vector(d2, 1.0)
ln2 = f.line(f.cartesian_point((1.0, 0.0, 0.0)), v2)
ec2 = f._emit_raw(
    f"EDGE_CURVE('v2check_e2',#{vV1.eid},#{vV2.eid},#{ln2.eid},.T.)"
)

# v2check_e3: V2 -> V3
d3  = f.direction((1.0, 0.0, 0.0))
v3  = f.vector(d3, 1.0)
ln3 = f.line(f.cartesian_point((2.0, 0.0, 0.0)), v3)
ec3 = f._emit_raw(
    f"EDGE_CURVE('v2check_e3',#{vV2.eid},#{vV3.eid},#{ln3.eid},.T.)"
)

oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# EDGE_LOOP: V2 appears 3 times — tests end-vertex extent symmetry IS detection defect
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi276.stp")
