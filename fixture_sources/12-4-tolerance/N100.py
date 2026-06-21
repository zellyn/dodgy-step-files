"""N100 — ShapeAnalysis_Edge.CheckPoints precision-asymmetry-extreme.

CheckPoints(P1A, P2A, P1B, P2B, preci1=1e-15, preci2=1.0) averages
precisions: (1e-15 + 1.0) / 2 ≈ 0.5. Neither tolerance enforced; masks both
extremes. E1 fails individual preci1 but passes average; E2 passes individual
preci2 but fails average. Result: asymmetric, false-negative verdicts.

Geometry: two edges with extreme asymmetric tolerances (1e-15 and 1.0 mm).

(No byte assertions; kernel-test-pair.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N100",
    defect=(
        "CheckPoints precision-asymmetry-extreme: two edges; "
        "preci1=1e-15 vs preci2=1.0; averaging masks both extremes; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# E1: ultra-tight tolerance context — endpoints separated by 1e-14.
p1A = f.cartesian_point((0.0, 0.0, 0.0), name="p1A")
p2A = f.cartesian_point((1.0e-14, 0.0, 0.0), name="p2A_ultra_close")
v1A = f.vertex_point(p1A, name="v1A")
v2A = f.vertex_point(p2A, name="v2A")
d1 = f.direction((1.0, 0.0, 0.0))
ln1 = f.line(p1A, f.vector(d1, 1.0e-14), name="ln_ultra_tight")
eA = f.edge_curve(v1A, v2A, ln1, name="eA_ultra_tight")

# E2: coarse tolerance context — endpoints separated by 0.9.
p1B = f.cartesian_point((0.0, 1.0, 0.0), name="p1B")
p2B = f.cartesian_point((0.9, 1.0, 0.0), name="p2B_coarse")
v1B = f.vertex_point(p1B, name="v1B")
v2B = f.vertex_point(p2B, name="v2B")
d2 = f.direction((1.0, 0.0, 0.0))
ln2 = f.line(p1B, f.vector(d2, 0.9), name="ln_coarse")
eB = f.edge_curve(v1B, v2B, ln2, name="eB_coarse")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('asymmetric_prec',(#{eA.eid},#{eB.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N100','N100','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Two extreme tolerance entries: ultra-tight and coarse.
unc1 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-15),#{lu.eid},"
    f"'distance_accuracy_value','ultra_tight_preci1')"
)
unc2 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0),#{lu.eid},"
    f"'distance_accuracy_value','coarse_preci2')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc1.eid},#{unc2.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
