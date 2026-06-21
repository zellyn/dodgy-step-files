"""N055 — ShapeFix_ShapeTolerance.LimitTolerance boundary ambiguity.

LimitTolerance permits tmax >= tmin, allowing equality case tmax == tmin.
When bounds are equal, newtol selection logic becomes nondeterministic:
clamping to tmin vs tmax yields identical result but invariant tmin < tmax
(strict ordering) is violated. Downstream code assumes strict ordering;
equality case creates ambiguity in tolerance domain membership.

Reproducer: Load N055.stp then call:
  ShapeFix_ShapeTolerance st;
  st.LimitTolerance(shape, 0.002, 0.002, TopAbs_VERTEX);
Condition (tmax >= tmin) satisfied; newtol selection cannot decide whether
to clamp to tmin or tmax (they are equal).

(No byte assertions; kernel-test-pair — defect requires LimitTolerance
runtime invocation with tmin == tmax == 0.002.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N055",
    defect=(
        "LimitTolerance input: single vertex at origin; tmin == tmax == 0.002; "
        "equality boundary makes newtol clamp nondeterministic; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# A single vertex at the origin — minimal shape for LimitTolerance input.
p_origin = f.cartesian_point((0.0, 0.0, 0.0), name="origin")
v_origin = f.vertex_point(p_origin, name="v_origin")

# A trivial line edge so we have a drawable entity.
p_end = f.cartesian_point((1.0, 0.0, 0.0), name="p_end")
v_end = f.vertex_point(p_end, name="v_end")
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 1.0)
ln = f.line(p_origin, vec, name="unit_line")
edge = f.edge_curve(v_origin, v_end, ln, name="edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('limit_tol_input',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N055','N055','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Both tmin and tmax = 0.002 — equality boundary.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(2.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','limit_tol_equal_bounds')"
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
