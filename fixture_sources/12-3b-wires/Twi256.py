"""Twi256 — ShapeAnalysis_Wire.CheckLoop.degenerated-edge-filter

Catalog claim: Wire with degenerate self-loop (1e-12 magnitude) plus normal
edge; validates degen filtering. Without BRep_Tool::Degenerated filter,
vertex extent inflates.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with two edges: a
degenerate 'degen_e' whose V1==V2 and whose LINE has magnitude 1e-12 (well
below any tolerance threshold), plus a normal 'normal_e' spanning 6 units.
When ShapeAnalysis_Wire::CheckLoop traverses the edge set it must detect
BRep_Tool::Degenerated() on 'degen_e' and skip it; without the filter the
degenerate vertex contributes to vertex extent inflation, masking real loop
geometry IS the defect.

Byte assertions:
  - contains(b'degen_e')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi256",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with degenerate and normal edges; "
        "degen_e: EDGE_CURVE V0->V0 (same vertex) LINE magnitude=1e-12 IS degenerate edge; "
        "normal_e: EDGE_CURVE V0->V1, LINE magnitude=6 IS normal edge; "
        "CheckLoop must call BRep_Tool::Degenerated() to filter degen_e; "
        "without filter vertex extent inflates IS loop-detection defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# Single vertex for the degenerate edge (V1 == V2)
vV0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
vV1 = f.vertex_point(f.cartesian_point((6.0, 0.0, 0.0)))

# degen_e: degenerate self-loop with 1e-12 magnitude IS the defect
# V1 == V2 == vV0; magnitude=1e-12 marks this as degenerate
degen_dir = f.direction((1.0, 0.0, 0.0))
degen_vec = f.vector(degen_dir, 1e-12)
degen_ln  = f.line(f.cartesian_point((0.0, 0.0, 0.0)), degen_vec)
ec_degen  = f._emit_raw(
    f"EDGE_CURVE('degen_e',#{vV0.eid},#{vV0.eid},#{degen_ln.eid},.T.)"
)

# normal_e: V0 -> V1, magnitude=6
norm_dir = f.direction((1.0, 0.0, 0.0))
norm_vec = f.vector(norm_dir, 6.0)
norm_ln  = f.line(f.cartesian_point((0.0, 0.0, 0.0)), norm_vec)
ec_norm  = f._emit_raw(
    f"EDGE_CURVE('normal_e',#{vV0.eid},#{vV1.eid},#{norm_ln.eid},.T.)"
)

oe_degen = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_degen.eid},.T.)")
oe_norm  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_norm.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_degen.eid},#{oe_norm.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi256.stp")
