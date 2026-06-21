"""N050 — File-supplied UNCERTAINTY_MEASURE_WITH_UNIT parsed but never consumed.

BRL-CAD step-g UncertaintyMeasureWithUnit::Load parses the declared tight
tolerance (1.0E-6 mm) but no downstream consumer reads it back; AdvancedFace
hard-codes m_tolerance = 1e-3. Sub-tolerance features collapse, slivers get
crushed, and tight-precision authoring intent is silently downgraded.

Byte assertions:
  contains(b'UNCERTAINTY_MEASURE_WITH_UNIT')
  contains(b'1.0E-6') or contains(b'1e-6')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N050",
    defect=(
        "UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6)) declared; "
        "BRL-CAD step-g hard-codes m_tolerance=1e-3, ignoring 1.0E-6; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Simple line edge for step-g to process at tight tolerance.
p_start = f.cartesian_point((0.0, 0.0, 0.0), name="p_start")
p_end = f.cartesian_point((1.0, 0.0, 0.0), name="p_end")
v_start = f.vertex_point(p_start, name="v_start")
v_end = f.vertex_point(p_end, name="v_end")
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 1.0)
ln = f.line(p_start, vec, name="unit_line")
edge = f.edge_curve(v_start, v_end, ln, name="edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('tight_tol_input',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N050','N050','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Tight 1.0E-6 mm tolerance — BRL-CAD ignores this, uses 1e-3.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
    f"'distance_accuracy_value','sub_micrometre_precision')"
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
