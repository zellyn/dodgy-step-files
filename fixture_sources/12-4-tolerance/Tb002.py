"""Tb002 — Sub-tolerance vertex gap that closes at 1e-7 but inflates at 1e-3.

Inverse of Tb001. Vertices are 5e-5 mm apart but the file declares 1e-7
uncertainty. A 1e-7 receiver treats them as separate (correctly). A receiver
that loosens tolerance to 1e-3 (e.g. downstream Boolean fuzzy ops) folds them
together, silently changing the topology. Three edges: two long ones and a
5e-5 mm bridge between the distinct vertices.

Byte assertions:
  contains(b'1.0E-7')
  count_entity_def(b'EDGE_CURVE') == 3
  count_entity_def(b'VERTEX_POINT') == 4

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb002",
    defect=(
        "two VERTEX_POINTs 5e-5 mm apart; declared uncertainty 1.0E-7 (strict) "
        "means they are distinct; lax receiver merging at 1e-3 corrupts topology; "
        "three EDGE_CURVEs including 5e-5 mm bridge; OCC yields empty"
    ),
)

# Vertices: a0 at (0,0,0), a1 at (10,0,0), b0 at (10.00005,0,0), b1 at (20.00005,0,0).
# Bridge edge: a1 -> b0, length 5e-5 mm.
pa0 = f.cartesian_point((0.0, 0.0, 0.0), name="a0")
pa1 = f.cartesian_point((10.0, 0.0, 0.0), name="a1")
pb0 = f.cartesian_point((10.00005, 0.0, 0.0), name="b0_5e-5_apart")
pb1 = f.cartesian_point((20.00005, 0.0, 0.0), name="b1")

va0 = f.vertex_point(pa0, name="va0")
va1 = f.vertex_point(pa1, name="va1_distinct")
vb0 = f.vertex_point(pb0, name="vb0_distinct")
vb1 = f.vertex_point(pb1, name="vb1")

# Edge A: (0,0,0) -> (10,0,0)
da = f.direction((1.0, 0.0, 0.0))
veca = f.vector(da, 10.0)
la = f.line(pa0, veca)
eA = f.edge_curve(va0, va1, la, name="eA")

# Bridge edge: (10,0,0) -> (10.00005,0,0), length 5e-5 mm
dbridge = f.direction((1.0, 0.0, 0.0))
vecbridge = f.vector(dbridge, 5.0e-5)
lbridge = f.line(pa1, vecbridge)
eBridge = f.edge_curve(va1, vb0, lbridge, name="eBridge_5e-5")

# Edge B: (10.00005,0,0) -> (20.00005,0,0)
db = f.direction((1.0, 0.0, 0.0))
vecb = f.vector(db, 10.0)
lb = f.line(pb0, vecb)
eB = f.edge_curve(vb0, vb1, lb, name="eB")

# GEOMETRIC_CURVE_SET for shape_null == True.
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('wire_set',(#{eA.eid},#{eBridge.eid},#{eB.eid}))"
)

# Manual PRODUCT chain with strict declared tolerance 1.0E-7.
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb002','Tb002','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
    f"'distance_accuracy_value','declared_strict_tolerance')"
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
