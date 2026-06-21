"""N156 — tolerance_asymmetry conflation.

Extreme precision asymmetry (preci1=1e-12, preci2=0.5) in CheckPoints logic;
dual squared-distance condition masks both tolerance extremes, creating
false-negative distance checks.

Geometry: two edges with extreme endpoint precision asymmetry — one vertex
ultra-tight (1e-12 mm), one very coarse (0.5 mm).

(No byte assertions; kernel-test-pair.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N156",
    defect=(
        "tolerance_asymmetry conflation: preci1=1e-12, preci2=0.5; "
        "dual squared-distance condition masks both extremes; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Edge with ultra-tight start and coarse end.
p_tight = f.cartesian_point((0.0, 0.0, 0.0), name="p_tight_preci1")
p_coarse = f.cartesian_point((1.0, 0.0, 0.0), name="p_coarse_preci2")
v_tight = f.vertex_point(p_tight, name="v_tight")
v_coarse = f.vertex_point(p_coarse, name="v_coarse")

d = f.direction((1.0, 0.0, 0.0))
edge = f.edge_curve(v_tight, v_coarse, f.line(p_tight, f.vector(d, 1.0)), name="edge_asym")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('tol_asym',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N156','N156','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Two extreme tolerance entries.
unc_tight = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-12),#{lu.eid},"
    f"'distance_accuracy_value','ultra_tight_preci1')"
)
unc_coarse = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(5.0E-1),#{lu.eid},"
    f"'distance_accuracy_value','coarse_preci2')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_tight.eid},#{unc_coarse.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
