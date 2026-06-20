"""Twi272 — CheckLoop Unloaded/Trivial

Catalog claim: Single-edge wire V1->V2. Tests guard against multi-vertex loop
detection on degenerate wire (<2 edges). Must skip analysis.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with a single edge
'loop_e1'. The wire has only one edge (V1->V2); the CheckLoop algorithm
requires at least 2 edges to perform multi-vertex loop detection — a trivial
wire with fewer edges must be skipped. GEOMETRIC_CURVE_SET yields empty on
import.

Byte assertions:
  - contains(b'loop_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi272",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with single edge; wire has only one edge (V1->V2); "
        "loop_e1: (0,0,0)->(1,0,0) single segment — trivial wire has <2 edges; "
        "CheckLoop must skip multi-vertex detection on degenerate wire IS guard defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_CURVE IS wired into EDGE_LOOP; never orphaned"
    ),
)

# Single-edge wire: V1 -> V2
vV1 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
vV2 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))

# loop_e1: V1 -> V2
d1  = f.direction((1.0, 0.0, 0.0))
v1  = f.vector(d1, 1.0)
ln1 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v1)
ec1 = f._emit_raw(
    f"EDGE_CURVE('loop_e1',#{vV1.eid},#{vV2.eid},#{ln1.eid},.T.)"
)

oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# Single-edge EDGE_LOOP — trivial wire IS the degenerate condition
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi272.stp")
