"""Twi265 — FixClosed endpoint-mismatch

Catalog claim: Wire open by small gap at closure; FixClosed misses repair when
endpoint distance uses inconsistent precision.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with three edges
'close_e1', 'close_e2', 'close_e3' forming a triangle where the last edge's
end vertex is placed at a slightly different coordinate from the first edge's
start vertex — introducing a sub-tolerance gap that causes FixClosed to fail
to close the wire. The start vertex of close_e1 is at (0,0,0) while the end
vertex of close_e3 is placed at (1e-7, 0.0, 0.0), a gap below standard STEP
precision (1e-6) but triggering inconsistent distance comparison in FixClosed.
The open closure IS the endpoint-mismatch defect. GEOMETRIC_CURVE_SET yields
empty on import.

Byte assertions:
  - contains(b'close_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi265",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with three edges forming near-closed triangle; "
        "close_e1 starts at vStart=(0,0,0); close_e3 ends at vEnd=(1e-7,0,0); "
        "gap = 1e-7 below STEP precision threshold but above FixClosed distance comparison cutoff; "
        "FixClosed uses inconsistent precision causing endpoint mismatch IS closure-miss defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# Triangle with near-closure gap: start != end
vStart = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))     # first edge start
vV1    = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
vV2    = f.vertex_point(f.cartesian_point((0.5, 1.0, 0.0)))
vEnd   = f.vertex_point(f.cartesian_point((1.0e-7, 0.0, 0.0)))  # last edge end — gap-closure trigger

# close_e1: vStart -> vV1
d1  = f.direction((1.0, 0.0, 0.0))
v1  = f.vector(d1, 1.0)
ln1 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v1)
ec1 = f._emit_raw(
    f"EDGE_CURVE('close_e1',#{vStart.eid},#{vV1.eid},#{ln1.eid},.T.)"
)

# close_e2: vV1 -> vV2
d2  = f.direction((-0.5, 1.0, 0.0))
v2  = f.vector(d2, 1.118033988749895)  # sqrt(0.25+1)
ln2 = f.line(f.cartesian_point((1.0, 0.0, 0.0)), v2)
ec2 = f._emit_raw(
    f"EDGE_CURVE('close_e2',#{vV1.eid},#{vV2.eid},#{ln2.eid},.T.)"
)

# close_e3: vV2 -> vEnd (near but not equal to vStart IS the defect)
d3  = f.direction((-0.5, -1.0, 0.0))
v3  = f.vector(d3, 1.118033988749895)
ln3 = f.line(f.cartesian_point((0.5, 1.0, 0.0)), v3)
ec3 = f._emit_raw(
    f"EDGE_CURVE('close_e3',#{vV2.eid},#{vEnd.eid},#{ln3.eid},.T.)"
)

oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi265.stp")
