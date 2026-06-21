"""Tb009 — Self-intersection visible at full precision but rounded out at receiver tolerance.

Two short edges cross in 3D at separation 3e-7 mm. Declared uncertainty is
1.0E-6 (looser than the crossing). A receiver rounding coordinates to 1e-6
working precision sees the edges as touching at a point (no self-intersection).
An exact-arithmetic receiver, or one with tol < 3e-7, sees the self-intersection.
Same input, two reports.

Byte assertions:
  count_entity_def(b'EDGE_CURVE') == 2
  contains(b'1.0E-6')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb009",
    defect=(
        "two EDGE_CURVEs crossing at 3.0E-7 mm separation below declared 1.0E-6 tolerance; "
        "receiver rounding to 1e-6 sees edges touching (no self-intersection); "
        "exact receiver sees self-intersection; GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Edge A: line from (0,0,0) to (1,0,0).
# Edge B: line from (0.5,-3.0E-7,0) to (0.5,1,0) -- starts 3e-7 below A.
pa0 = f.cartesian_point((0.0, 0.0, 0.0), name="a0")
pa1 = f.cartesian_point((1.0, 0.0, 0.0), name="a1")
pb0 = f.cartesian_point((0.5, -3.0e-7, 0.0), name="b0_below_3e-7")
pb1 = f.cartesian_point((0.5, 1.0, 0.0), name="b1")

va0 = f.vertex_point(pa0, name="va0")
va1 = f.vertex_point(pa1, name="va1")
vb0 = f.vertex_point(pb0, name="vb0")
vb1 = f.vertex_point(pb1, name="vb1")

da = f.direction((1.0, 0.0, 0.0))
veca = f.vector(da, 1.0)
la = f.line(pa0, veca)
eA = f.edge_curve(va0, va1, la, name="eA")

db = f.direction((0.0, 1.0, 0.0))
vecb = f.vector(db, 1.0 + 3.0e-7)
lb = f.line(pb0, vecb)
eB = f.edge_curve(vb0, vb1, lb, name="eB")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('cs',(#{eA.eid},#{eB.eid}))")

# Manual PRODUCT chain with declared tolerance 1.0E-6.
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb009','Tb009','',(#{prod_ctx.eid}))")
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
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
    f"'distance_accuracy_value','tol_above_intersection_separation')"
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
