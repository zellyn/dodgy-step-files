"""N002 — Wireframe gap-fix inflates tolerance instead of bridging the gap.

A wireframe gap-fixing pass increases the maximum tolerance carried by edges
and vertices to encompass the gap (2.0E-3), rather than adjusting the underlying
geometry to close it. The wire's declared model uncertainty is only 1.0E-6.

Two EDGE_CURVEs share a logical junction but have separate VERTEX_POINTs
1.0E-3 mm apart; the gap-fix has raised the declared tolerance to 2.0E-3 to
swallow the gap instead of closing it geometrically.

Byte assertions:
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 2
  contains(b'1.0E-6') and contains(b'2.0E-3')
  count_entity_def(b'EDGE_CURVE') == 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N002",
    defect=(
        "gap-fix inflates declared tolerance to 2.0E-3 to cover 1.0E-3 gap; "
        "model uncertainty 1.0E-6; two EDGE_CURVEs with 1.0E-3 mm gap at junction; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Edge A: (0,0,0) -> (10,0,0)
pa0 = f.cartesian_point((0.0, 0.0, 0.0), name="pa0")
pa1 = f.cartesian_point((10.0, 0.0, 0.0), name="pa1")
va0 = f.vertex_point(pa0, name="va0")
va1 = f.vertex_point(pa1, name="va1")
da = f.direction((1.0, 0.0, 0.0))
veca = f.vector(da, 10.0)
la = f.line(pa0, veca)
eA = f.edge_curve(va0, va1, la, name="eA")

# Edge B: gap junction at (10.001, 0, 0) — 1e-3 mm gap from va1
pb0 = f.cartesian_point((10.001, 0.0, 0.0), name="pb0_gap_1e-3")
pb1 = f.cartesian_point((20.001, 0.0, 0.0), name="pb1")
vb0 = f.vertex_point(pb0, name="vb0_gap")
vb1 = f.vertex_point(pb1, name="vb1")
db = f.direction((1.0, 0.0, 0.0))
vecb = f.vector(db, 10.0)
lb = f.line(pb0, vecb)
eB = f.edge_curve(vb0, vb1, lb, name="eB")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('wire',(#{eA.eid},#{eB.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N002','N002','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# Two UNCERTAINTY_MEASURE_WITH_UNIT: original 1.0E-6 and inflated 2.0E-3.
unc_orig = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
    f"'distance_accuracy_value','original_model_uncertainty')"
)
unc_inflated = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(2.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','gap_fix_inflated_tolerance')"
)

ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_orig.eid},#{unc_inflated.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
