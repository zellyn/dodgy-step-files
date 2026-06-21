"""Tb001 — Sub-tolerance vertex gap that closes at 1e-3 but yawns open at 1e-7.

Two EDGE_CURVEs share endpoints logically but with separate VERTEX_POINTs
5e-5 mm apart. Declared UNCERTAINTY_MEASURE_WITH_UNIT is 1e-3. A receiver
honouring the declared tolerance treats the vertices as coincident (wire
closed). A receiver hardcoding Precision::Confusion (~1e-7) sees a gap
(free-edge / naked-edge defect). Simultaneously valid and invalid depending
on tolerance interpretation; a classic round-trip time bomb.

Byte assertions:
  contains(b'1.0E-3')
  count_entity_def(b'EDGE_CURVE') == 2
  count_entity_def(b'VERTEX_POINT') == 4

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb001",
    defect=(
        "two VERTEX_POINTs 5e-5 mm apart on end-to-end EDGE_CURVEs; "
        "declared uncertainty 1.0E-3 — vertex gap is sub-tolerance so wire "
        "appears closed; hardcoded Precision::Confusion ~1e-7 sees a gap; "
        "GEOMETRIC_CURVE_SET as model root — OCC yields empty"
    ),
)

# Geometry: two line edges with a 5e-5 mm gap between their end vertices.
# Edge A: (0,0,0) -> (10,0,0)
# Edge B: (10.00005,0,0) -> (20.00005,0,0)  [gap = 5e-5 mm]
pa0 = f.cartesian_point((0.0, 0.0, 0.0), name="a0")
pa1 = f.cartesian_point((10.0, 0.0, 0.0), name="a1")
pb0 = f.cartesian_point((10.00005, 0.0, 0.0), name="b0_gap_5e-5")
pb1 = f.cartesian_point((20.00005, 0.0, 0.0), name="b1")

va0 = f.vertex_point(pa0, name="va0")
va1 = f.vertex_point(pa1, name="va1")
vb0 = f.vertex_point(pb0, name="vb0_at_gap")
vb1 = f.vertex_point(pb1, name="vb1")

# Line A
da = f.direction((1.0, 0.0, 0.0))
veca = f.vector(da, 10.0)
la = f.line(pa0, veca)
eA = f.edge_curve(va0, va1, la, name="eA")

# Line B
db = f.direction((1.0, 0.0, 0.0))
vecb = f.vector(db, 10.0)
lb = f.line(pb0, vecb)
eB = f.edge_curve(vb0, vb1, lb, name="eB")

# Wrap in a GEOMETRIC_CURVE_SET so OCC produces empty (shape_null == True).
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('wire_set',(#{eA.eid},#{eB.eid}))")

# Manual PRODUCT chain with uncertainty 1.0E-3 (declared loose tolerance).
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb001','Tb001','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')")
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Declared loose tolerance: 1.0E-3 — the key byte assertion value.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','declared_loose_tolerance')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
