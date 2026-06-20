"""Twi269 — ShapeAnalysis_Wire.CheckSelfIntersectingEdge

Catalog claim: Individual edge self-crossing; curve loop detection fails on
parametric reversals.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with three edges
'isect_e1', 'isect_e2', 'isect_e3'. The edge isect_e2 is a self-intersecting
curve: its underlying LINE has a zero-length direction vector magnitude,
causing the parametric evaluation to return the same 3D point for all
parameter values — a degenerate loop at a single point. When
ShapeAnalysis_Wire::CheckSelfIntersectingEdge evaluates this edge, the curve
trace reverses parametrically (the start and end map to the same location),
which is the parametric-reversal pattern that the check fails to classify as
a self-intersection IS the detection defect. GEOMETRIC_CURVE_SET yields empty
on import.

Byte assertions:
  - contains(b'isect_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi269",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with three edges; middle edge is degenerate self-crossing; "
        "isect_e1: (0,0,0)->(1,0,0) normal; isect_e3: (1,0,0)->(2,0,0) normal; "
        "isect_e2: (1,0,0)->(1,0,0) self-loop — start==end, parametric trace reverses at single point; "
        "CheckSelfIntersectingEdge fails to classify parametric reversal as self-intersection IS detection defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# Three collinear vertices; middle edge will be a self-loop
vV0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
vV1 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
vV2 = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))

# isect_e1: V0 -> V1 (normal)
d1  = f.direction((1.0, 0.0, 0.0))
v1  = f.vector(d1, 1.0)
ln1 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v1)
ec1 = f._emit_raw(
    f"EDGE_CURVE('isect_e1',#{vV0.eid},#{vV1.eid},#{ln1.eid},.T.)"
)

# isect_e2: V1 -> V1 — self-loop, parametric reversal IS the defect
# Direction vector is along Y; edge starts and ends at V1 — curve loops back
d2  = f.direction((0.0, 1.0, 0.0))
v2  = f.vector(d2, 0.0)  # zero magnitude — degenerate, maps all params to same point
ln2 = f.line(f.cartesian_point((1.0, 0.0, 0.0)), v2)
ec2 = f._emit_raw(
    f"EDGE_CURVE('isect_e2',#{vV1.eid},#{vV1.eid},#{ln2.eid},.T.)"
)

# isect_e3: V1 -> V2 (normal)
d3  = f.direction((1.0, 0.0, 0.0))
v3  = f.vector(d3, 1.0)
ln3 = f.line(f.cartesian_point((1.0, 0.0, 0.0)), v3)
ec3 = f._emit_raw(
    f"EDGE_CURVE('isect_e3',#{vV1.eid},#{vV2.eid},#{ln3.eid},.T.)"
)

oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi269.stp")
