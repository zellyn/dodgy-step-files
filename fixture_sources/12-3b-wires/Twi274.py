"""Twi274 — CheckLoop Seam Classification

Catalog claim: Wire on closed surface: regular edge + seam (V->V). Seam must
exclude from loop degree count. Without filter, spurious multi-vertex detection.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with two edges: a
regular edge 'seam_reg' (V0->V1) and a seam edge 'seam_seam' (V1->V1, a
self-loop back to the same vertex). The seam edge traverses the periodic seam
of a closed surface but topologically connects V1 to itself. The CheckLoop
algorithm must detect and exclude seam edges from the loop degree count;
without the seam filter, the self-loop at V1 triggers spurious multi-vertex
detection. GEOMETRIC_CURVE_SET yields empty on import.

Byte assertions:
  - contains(b'seam_reg')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi274",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with two edges; regular edge + seam (V->V self-loop); "
        "seam_reg: (0,0,0)->(1,0,0) normal edge; "
        "seam_seam: (1,0,0)->(1,0,0) seam self-loop — same vertex at start and end; "
        "CheckLoop must exclude seam edges from loop degree count IS spurious detection defect; "
        "without seam filter, self-loop at V1 triggers spurious multi-vertex detection; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# Two vertices: V0 and V1
vV0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
vV1 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))

# seam_reg: V0 -> V1 (regular edge)
d1  = f.direction((1.0, 0.0, 0.0))
v1  = f.vector(d1, 1.0)
ln1 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v1)
ec1 = f._emit_raw(
    f"EDGE_CURVE('seam_reg',#{vV0.eid},#{vV1.eid},#{ln1.eid},.T.)"
)

# seam_seam: V1 -> V1 (seam self-loop — traverses periodic seam, same vertex)
d2  = f.direction((0.0, 1.0, 0.0))
v2  = f.vector(d2, 1.0)
ln2 = f.line(f.cartesian_point((1.0, 0.0, 0.0)), v2)
ec2 = f._emit_raw(
    f"EDGE_CURVE('seam_seam',#{vV1.eid},#{vV1.eid},#{ln2.eid},.T.)"
)

oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# EDGE_LOOP: regular edge + seam self-loop IS the seam classification test
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi274.stp")
