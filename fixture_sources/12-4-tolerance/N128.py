"""N128 — ShapeFix_ShapeTolerance.LimitTolerance boundary-equality-nondeterminism.

LimitTolerance allows tmax == tmin without semantic enforcement. Tolerance
clamping becomes nondeterministic when bounds collapse; newtol selection
between tmin/tmax unpredictable. Code checks iamax = (tmax >= tmin) but not
tmax > tmin strictly.

Geometry: single edge with tolerance in [0.001, 0.005]; LimitTolerance called
with tmin==tmax==0.003 (equal bounds).

(No byte assertions; kernel-test-pair — defect requires LimitTolerance runtime
invocation with equal min/max bounds.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N128",
    defect=(
        "LimitTolerance boundary-equality-nondeterminism: single edge; "
        "LimitTolerance(shape, 0.003, 0.003) — iamax condition (>=) satisfied "
        "but newtol selection nondeterministic; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Single edge with tolerance in range [0.001, 0.005].
p_start = f.cartesian_point((0.0, 0.0, 0.0), name="p_start")
p_end = f.cartesian_point((5.0, 0.0, 0.0), name="p_end")
v_start = f.vertex_point(p_start, name="v_start")
v_end = f.vertex_point(p_end, name="v_end")
d = f.direction((1.0, 0.0, 0.0))
ln = f.line(p_start, f.vector(d, 5.0), name="line")
edge = f.edge_curve(v_start, v_end, ln, name="edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('boundary_eq',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N128','N128','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# File declares 0.003 as midpoint of the [0.001,0.005] range.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(3.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','limit_tol_equal_boundary')"
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
