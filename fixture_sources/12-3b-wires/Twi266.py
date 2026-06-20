"""Twi266 — FixGap3d parameter-discontinuity

Catalog claim: Wire with 3D curve reversing at edge junction; FixGap3d fails
to detect reversals violating parametric continuity.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with three edges
'gap3d_e1', 'gap3d_e2', 'gap3d_e3'. The edges are topologically connected
(shared vertex entities), but gap3d_e2 has its underlying LINE direction
reversed — the parametric direction goes from the end back toward the start,
violating the expected parametric continuity at the junction. FixGap3d checks
3D gap distances between edge endpoints but does not check parametric
reversal, so the reversal IS missed. The reversed parametric direction on the
middle edge IS the parameter-discontinuity defect. GEOMETRIC_CURVE_SET yields
empty on import.

Byte assertions:
  - contains(b'gap3d_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi266",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with three edges; middle edge parametrically reversed; "
        "gap3d_e1: (0,0,0)->(1,0,0); gap3d_e2: (1,0,0)->(2,0,0) but LINE direction is (-1,0,0) reversed; "
        "gap3d_e3: (2,0,0)->(2,1,0); FixGap3d checks 3D endpoint gaps not parametric direction; "
        "reversed direction on gap3d_e2 violates parametric continuity IS gap3d-miss defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# Three vertices forming an L-shape path
vV0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
vV1 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
vV2 = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))
vV3 = f.vertex_point(f.cartesian_point((2.0, 1.0, 0.0)))

# gap3d_e1: V0 -> V1 (normal direction)
d1  = f.direction((1.0, 0.0, 0.0))
v1  = f.vector(d1, 1.0)
ln1 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v1)
ec1 = f._emit_raw(
    f"EDGE_CURVE('gap3d_e1',#{vV0.eid},#{vV1.eid},#{ln1.eid},.T.)"
)

# gap3d_e2: V1 -> V2, but LINE direction is reversed (-1,0,0) IS the defect
# The EDGE_CURVE still nominally runs V1->V2 but underlying curve direction is reversed
d2  = f.direction((-1.0, 0.0, 0.0))
v2  = f.vector(d2, 1.0)
ln2 = f.line(f.cartesian_point((2.0, 0.0, 0.0)), v2)  # starts at end point, going reversed
ec2 = f._emit_raw(
    f"EDGE_CURVE('gap3d_e2',#{vV1.eid},#{vV2.eid},#{ln2.eid},.T.)"
)

# gap3d_e3: V2 -> V3 (normal direction)
d3  = f.direction((0.0, 1.0, 0.0))
v3  = f.vector(d3, 1.0)
ln3 = f.line(f.cartesian_point((2.0, 0.0, 0.0)), v3)
ec3 = f._emit_raw(
    f"EDGE_CURVE('gap3d_e3',#{vV2.eid},#{vV3.eid},#{ln3.eid},.T.)"
)

oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi266.stp")
