"""Twi261 — dual-vertex-binding

Catalog claim: Three edges with V2 having three incident edges (Extent=3).
Both V1 and V2 lists must be appended; asymmetric append loses degree count.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with three non-self-loop
edges: 'edge_a' (V0->V1), 'edge_b' (V1->V2), 'edge_c' (V1->V0). All three
edges share vertex V1 as an endpoint (V1 appears as V2 in edge_a, V1 in
edge_b, V1 in edge_c). For non-self-loop edges, CheckLoop must append to
both the V1 list and the V2 list; if only V1 is appended, V1's extent count
stays at 1 instead of 3, and the multi-vertex detection fails IS the defect.

Byte assertions:
  - contains(b'edge_a')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi261",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with three edges sharing vertex V1; "
        "edge_a: V0->V1; edge_b: V1->V2; edge_c: V1->V0 — V1 has degree 3 (Extent=3); "
        "CheckLoop must append non-self-loop edges to both V1 and V2 endpoint lists; "
        "asymmetric append (V1 only) undercounts V1 degree IS dual-vertex-binding defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# Three vertices; V1 is the high-degree vertex
vV0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
vV1 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
vV2 = f.vertex_point(f.cartesian_point((1.0, 1.0, 0.0)))

# edge_a: V0 -> V1
d_a  = f.direction((1.0, 0.0, 0.0))
v_a  = f.vector(d_a, 1.0)
ln_a = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v_a)
ec_a = f._emit_raw(
    f"EDGE_CURVE('edge_a',#{vV0.eid},#{vV1.eid},#{ln_a.eid},.T.)"
)

# edge_b: V1 -> V2
d_b  = f.direction((0.0, 1.0, 0.0))
v_b  = f.vector(d_b, 1.0)
ln_b = f.line(f.cartesian_point((1.0, 0.0, 0.0)), v_b)
ec_b = f._emit_raw(
    f"EDGE_CURVE('edge_b',#{vV1.eid},#{vV2.eid},#{ln_b.eid},.T.)"
)

# edge_c: V1 -> V0 (back edge — makes V1 degree-3)
d_c  = f.direction((-1.0, 0.0, 0.0))
v_c  = f.vector(d_c, 1.0)
ln_c = f.line(f.cartesian_point((1.0, 0.0, 0.0)), v_c)
ec_c = f._emit_raw(
    f"EDGE_CURVE('edge_c',#{vV1.eid},#{vV0.eid},#{ln_c.eid},.T.)"
)

oe_a = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_a.eid},.T.)")
oe_b = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_b.eid},.T.)")
oe_c = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_c.eid},.T.)")

loop = f._emit_raw(f"EDGE_LOOP('',(#{oe_a.eid},#{oe_b.eid},#{oe_c.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi261.stp")
