"""N163 — precision_tolerance mixed-unit-scale mismatch.

Tolerance declared in metre (1e-7) unscaled against millimetre coordinates
(1.0). Factor-of-10000 discrepancy (1 mm geometry vs 1e-7 metre context =
1e-4 mm vs 1.0 mm — 10000× off). Tests unit consistency in precision handling.

Geometry: millimetre-scale edge (1 mm length) with UNCERTAINTY_MEASURE
declared as if in metres (1e-7 m = 1e-4 mm), creating 10000× mismatch
when the context unit is millimetres.

(No byte assertions; kernel-test-pair — defect requires precision comparison
against unscaled metre tolerance in mm-unit context.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N163",
    defect=(
        "precision_tolerance mixed-unit-scale: 1mm edge; tol declared 1e-7 "
        "(as metres = 1e-4 mm); 10000x discrepancy against mm coords; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# 1 mm edge in millimetre coordinates.
p_start = f.cartesian_point((0.0, 0.0, 0.0), name="p_start")
p_end = f.cartesian_point((1.0, 0.0, 0.0), name="p_end_1mm")
v_start = f.vertex_point(p_start, name="v_start")
v_end = f.vertex_point(p_end, name="v_end")
d = f.direction((1.0, 0.0, 0.0))
edge = f.edge_curve(v_start, v_end, f.line(p_start, f.vector(d, 1.0)), name="edge_1mm")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('unit_mismatch',(#{edge.eid}))")

app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N163','N163','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')")
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Tolerance declared as 1e-7 "metres" (unscaled) in a mm-unit context.
# 1e-7 metres = 1e-4 mm; against 1.0 mm geometry = 10000× mismatch.
unc = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},'distance_accuracy_value','metre_unscaled_in_mm_context')")
ctx = f._emit_raw(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))REPRESENTATION_CONTEXT('ctx','3D'))")
wfr = f._emit_raw(f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})")
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
