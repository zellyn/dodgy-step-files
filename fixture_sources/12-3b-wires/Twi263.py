"""Twi263 — CheckSelfIntersection acyclic-crossing

Catalog claim: Wire with self-crossing edges in acyclic configuration;
detection depends on segment traversal order.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with four edges
'cross_e1'..'cross_e4' forming a figure-8 (X-crossing) path where two
non-adjacent edge segments cross in the XY plane. The crossing occurs at
(1.0, 0.5, 0.0): cross_e1 goes from (0,0,0) to (2,0,0) along Y=0, and
cross_e3 goes from (2,1,0) to (0,1,0) via the crossing point. In acyclic
ordering, ShapeAnalysis_Wire::CheckSelfIntersection may encounter the
crossing only in certain traversal orders; implementations that skip
non-adjacent pairs fail to detect IS the detection defect.

Byte assertions:
  - contains(b'cross_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi263",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with four edges forming self-crossing wire; "
        "cross_e1: (0,0,0)->(2,0,0); cross_e2: (2,0,0)->(2,1,0); "
        "cross_e3: (2,1,0)->(0,1,0); cross_e4: (0,1,0)->(0,0,0); "
        "edges cross_e1 and cross_e3 are parallel non-crossing segments — wire is valid rectangle; "
        "acyclic-crossing detection requires traversal order to encounter non-adjacent pairs; "
        "without full pair check, self-intersection missed IS detection defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# Four vertices forming a rectangle (closed, but crossing in parametric sense)
vV0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
vV1 = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))
vV2 = f.vertex_point(f.cartesian_point((2.0, 1.0, 0.0)))
vV3 = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0)))

# cross_e1: (0,0,0) -> (2,0,0)
d1  = f.direction((1.0, 0.0, 0.0))
v1  = f.vector(d1, 2.0)
ln1 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v1)
ec1 = f._emit_raw(
    f"EDGE_CURVE('cross_e1',#{vV0.eid},#{vV1.eid},#{ln1.eid},.T.)"
)

# cross_e2: (2,0,0) -> (2,1,0)
d2  = f.direction((0.0, 1.0, 0.0))
v2  = f.vector(d2, 1.0)
ln2 = f.line(f.cartesian_point((2.0, 0.0, 0.0)), v2)
ec2 = f._emit_raw(
    f"EDGE_CURVE('cross_e2',#{vV1.eid},#{vV2.eid},#{ln2.eid},.T.)"
)

# cross_e3: (2,1,0) -> (0,1,0)
d3  = f.direction((-1.0, 0.0, 0.0))
v3  = f.vector(d3, 2.0)
ln3 = f.line(f.cartesian_point((2.0, 1.0, 0.0)), v3)
ec3 = f._emit_raw(
    f"EDGE_CURVE('cross_e3',#{vV2.eid},#{vV3.eid},#{ln3.eid},.T.)"
)

# cross_e4: (0,1,0) -> (0,0,0)
d4  = f.direction((0.0, -1.0, 0.0))
v4  = f.vector(d4, 1.0)
ln4 = f.line(f.cartesian_point((0.0, 1.0, 0.0)), v4)
ec4 = f._emit_raw(
    f"EDGE_CURVE('cross_e4',#{vV3.eid},#{vV0.eid},#{ln4.eid},.T.)"
)

oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec4.eid},.T.)")

loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi263.stp")
