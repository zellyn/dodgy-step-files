"""Twi271 — ShapeAnalysis_Wire.CheckTail

Catalog claim: Wire terminus validation; tail edge proximity check fails when
endpoint gaps exceed local curve curvature radius.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with three edges
'tail_e1', 'tail_e2', 'tail_e3'. The wire is open — tail_e3 ends at a vertex
vTail that is displaced by a gap larger than the local curvature radius of
the endpoint curve but still smaller than the global wire tolerance. The
CheckTail algorithm uses curvature-radius-relative proximity: the gap distance
is computed as a fraction of the local curvature radius at the endpoint. When
the gap exceeds the curvature radius (gap > R_curv), the tail condition is
active but the check fails to flag it because the absolute distance comparison
dominates IS the proximity-check defect. GEOMETRIC_CURVE_SET yields empty on
import.

Byte assertions:
  - contains(b'tail_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi271",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with three edges; last edge ends at displaced tail vertex; "
        "tail_e1: (0,0,0)->(1,0,0); tail_e2: (1,0,0)->(1,1,0); "
        "tail_e3: (1,1,0)->vTail=(0.5,0.5,0.0) — tail displaced by 0.5 from wire start at (0,0,0); "
        "gap=0.5 exceeds local curvature radius at endpoint IS tail proximity failure; "
        "CheckTail uses curvature-radius comparison; absolute distance dominates IS proximity-check defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# Open wire with a tail — last vertex is not at wire start
vV0   = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))   # wire start
vV1   = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
vV2   = f.vertex_point(f.cartesian_point((1.0, 1.0, 0.0)))
vTail = f.vertex_point(f.cartesian_point((0.5, 0.5, 0.0)))   # tail end — displaced from vV0

# tail_e1: V0 -> V1
d1  = f.direction((1.0, 0.0, 0.0))
v1  = f.vector(d1, 1.0)
ln1 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v1)
ec1 = f._emit_raw(
    f"EDGE_CURVE('tail_e1',#{vV0.eid},#{vV1.eid},#{ln1.eid},.T.)"
)

# tail_e2: V1 -> V2
d2  = f.direction((0.0, 1.0, 0.0))
v2  = f.vector(d2, 1.0)
ln2 = f.line(f.cartesian_point((1.0, 0.0, 0.0)), v2)
ec2 = f._emit_raw(
    f"EDGE_CURVE('tail_e2',#{vV1.eid},#{vV2.eid},#{ln2.eid},.T.)"
)

# tail_e3: V2 -> vTail — open wire tail IS the terminus defect
d3  = f.direction((-0.5, -0.5, 0.0))
v3  = f.vector(d3, 0.7071067811865476)  # sqrt(0.5)
ln3 = f.line(f.cartesian_point((1.0, 1.0, 0.0)), v3)
ec3 = f._emit_raw(
    f"EDGE_CURVE('tail_e3',#{vV2.eid},#{vTail.eid},#{ln3.eid},.T.)"
)

oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# Open EDGE_LOOP — tail vertex does not close to wire start IS the tail defect
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi271.stp")
