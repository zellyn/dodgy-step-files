"""N165 — tolerance_conservatism no safety margin.

Distance 0.099999 mm compared against 0.1 mm tolerance without margin buffer.
Single-ULP boundary case. Tests conservative threshold application.

Geometry: two edges 0.099999 mm apart — 1 ULP below the 0.1 mm tolerance.
Without a safety margin buffer, floating-point rounding can flip the
acceptance decision.

(No byte assertions; kernel-test-pair — defect requires distance comparison
at single-ULP boundary.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N165",
    defect=(
        "tolerance_conservatism no_safety_margin: 2 edges 0.099999mm apart; "
        "tol=0.1mm; single-ULP boundary; no margin buffer; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Two parallel edges 0.099999 mm apart (1 ULP below 0.1 mm threshold).
p0a = f.cartesian_point((0.0, 0.0, 0.0), name="p0a")
p1a = f.cartesian_point((1.0, 0.0, 0.0), name="p1a")
p0b = f.cartesian_point((0.0, 0.099999, 0.0), name="p0b_ulp")
p1b = f.cartesian_point((1.0, 0.099999, 0.0), name="p1b_ulp")

v0a = f.vertex_point(p0a, name="v0a")
v1a = f.vertex_point(p1a, name="v1a")
v0b = f.vertex_point(p0b, name="v0b")
v1b = f.vertex_point(p1b, name="v1b")

d = f.direction((1.0, 0.0, 0.0))
eA = f.edge_curve(v0a, v1a, f.line(p0a, f.vector(d, 1.0)), name="eA")
eB = f.edge_curve(v0b, v1b, f.line(p0b, f.vector(d, 1.0)), name="eB_ulp")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('ulp_boundary',(#{eA.eid},#{eB.eid}))")

app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N165','N165','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')")
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Tolerance 0.1 mm — edge separation 0.099999 mm is 1 ULP below.
unc = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-1),#{lu.eid},'distance_accuracy_value','tol_boundary')")
ctx = f._emit_raw(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))REPRESENTATION_CONTEXT('ctx','3D'))")
wfr = f._emit_raw(f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})")
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
