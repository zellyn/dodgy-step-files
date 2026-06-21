"""N162 — tolerance_selection coarse fallback unvalidated.

Fine tolerance unavailable; fallback to coarse without magnitude check.
0.1 mm coarse applied without confirming safety. Tests ShapeAnalysis
precision fallback logic.

Geometry: two edges where fine-precision is unavailable and coarse 0.1 mm
fallback is applied without magnitude safety check.

(No byte assertions; kernel-test-pair — defect requires ShapeAnalysis
precision fallback at runtime.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N162",
    defect=(
        "tolerance_selection coarse_fallback unvalidated: fine tol unavailable; "
        "coarse 0.1mm applied without magnitude check; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Two edges; coarse (0.1 mm) and fine (1e-7 mm) declared for fallback context.
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((1.0, 0.0, 0.0), name="p1")
p2 = f.cartesian_point((1.0, 1.0, 0.0), name="p2")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
v2 = f.vertex_point(p2, name="v2")

d_x = f.direction((1.0, 0.0, 0.0))
d_y = f.direction((0.0, 1.0, 0.0))
e0 = f.edge_curve(v0, v1, f.line(p0, f.vector(d_x, 1.0)), name="e0_coarse")
e1 = f.edge_curve(v1, v2, f.line(p1, f.vector(d_y, 1.0)), name="e1_fine")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('coarse_fallback',(#{e0.eid},#{e1.eid}))")

app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N162','N162','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')")
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Coarse tolerance that replaces unavailable fine tolerance.
unc_coarse = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-1),#{lu.eid},'distance_accuracy_value','coarse_fallback_tol')")
unc_fine = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},'distance_accuracy_value','unavailable_fine_tol')")
ctx = f._emit_raw(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_coarse.eid},#{unc_fine.eid}))GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))REPRESENTATION_CONTEXT('ctx','3D'))")
wfr = f._emit_raw(f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})")
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
