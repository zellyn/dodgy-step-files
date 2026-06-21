"""N015 — xstep.cascade.unit M meters setting inflates tolerance and corrupts geometry.

Setting OCCT's cascade unit to meters during STEP read inflates max-tolerance
(some files balloon AABB to ±1e+100). With unit=M, too-small distances are not
detected during edge reordering and BSpline segments are missed. The file
declares 1.0E-7 mm precision, but metric-mode tolerance scaling pushes the
working threshold below kernel resolution.

Byte assertions:
  contains(b'1.0E-7')
  count_entity_def(b'EDGE_CURVE') == 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N015",
    defect=(
        "cascade unit M inflation: file declares 1.0E-7 precision but M-mode "
        "scales tolerance below kernel resolution; single EDGE_CURVE; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Single edge: LINE (0,0,0) -> (1000,0,0) (1m in mm).
# In meters mode this would be 1.0 m; the issue is the working tolerance.
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((1000.0, 0.0, 0.0), name="p1_1m")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")

d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 1000.0)
line = f.line(p0, vec, name="line_1m")
edge = f.edge_curve(v0, v1, line, name="edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('edges',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N015','N015','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Declared tolerance 1.0E-7 — in M-mode this scales below kernel resolution.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
    f"'distance_accuracy_value','precision_below_M_mode_threshold')"
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
