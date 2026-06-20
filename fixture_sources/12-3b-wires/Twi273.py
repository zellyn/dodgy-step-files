"""Twi273 — CheckLoop Null Vertices

Catalog claim: Edge with null V1 vertex. Tests null-check guard that encodes
FAIL2 status before dereference. Prevents segfault.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with two edges where
'null_e1' has its V1 (start) vertex reference set to $ (unset/null). The
CheckLoop algorithm must test for null vertex references and encode FAIL2
status before attempting dereference — without the guard, a null dereference
causes a segfault. GEOMETRIC_CURVE_SET yields empty on import.

Byte assertions:
  - contains(b'null_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi273",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with two edges; null_e1 has null V1 vertex ($); "
        "null_e1: $->(1,0,0) — start vertex unset (null reference); "
        "null_e2: (1,0,0)->(2,0,0) normal; "
        "CheckLoop must null-check vertex refs and encode FAIL2 before dereference IS segfault guard; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# null_e1 has null start vertex — V1 is $
# Only define the end vertex; start vertex intentionally unset
vV2 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
vV3 = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))

# null_e1: $ -> vV2 — null start vertex IS the defect
d1  = f.direction((1.0, 0.0, 0.0))
v1  = f.vector(d1, 1.0)
ln1 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v1)
ec1 = f._emit_raw(
    f"EDGE_CURVE('null_e1',$,#{vV2.eid},#{ln1.eid},.T.)"
)

# null_e2: vV2 -> vV3 (normal)
d2  = f.direction((1.0, 0.0, 0.0))
v2  = f.vector(d2, 1.0)
ln2 = f.line(f.cartesian_point((1.0, 0.0, 0.0)), v2)
ec2 = f._emit_raw(
    f"EDGE_CURVE('null_e2',#{vV2.eid},#{vV3.eid},#{ln2.eid},.T.)"
)

oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# EDGE_LOOP with null-vertex edge IS the null-dereference guard test
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi273.stp")
