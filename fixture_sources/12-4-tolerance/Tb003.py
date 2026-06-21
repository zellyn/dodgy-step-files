"""Tb003 — Vertex-edge-face tolerance hierarchy holds in mm but inverts in m.

Three UNCERTAINTY_MEASURE_WITH_UNIT records (1e-6, 1e-5, 1e-4) represent
vertex/edge/face tolerances. The hierarchy tol(V) <= tol(E) <= tol(F) holds
in mm. A receiver rescaling to meters divides all by 1e3 to get 1e-9/1e-8/1e-7;
if the receiver then floors at a working-precision minimum (~1e-9), the floor
flattens the vertex value and may invert the hierarchy. Same input, two scaling
policies, two post-import hierarchies.

Byte assertions:
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 3
  contains(b'1.0E-6') and contains(b'1.0E-5') and contains(b'1.0E-4')
  contains(b'.MILLI.')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb003",
    defect=(
        "three UNCERTAINTY_MEASURE_WITH_UNIT at 1.0E-6/1.0E-5/1.0E-4 mm; "
        "hierarchy holds in mm; rescaling to meters without atomic tolerance "
        "rescale inverts the hierarchy; OCC yields empty"
    ),
)

# Minimal wire geometry so OCC gives empty (shape_null == True).
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 10.0)
line = f.line(p0, vec)
edge = f.edge_curve(v0, v1, line)
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('wire_set',(#{edge.eid}))")

# Manual PRODUCT chain with three-tier uncertainty hierarchy.
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb003','Tb003','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

# LENGTH_UNIT must declare .MILLI. (byte assertion: contains(b'.MILLI.')).
lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# Three UNCERTAINTY_MEASURE_WITH_UNIT: vertex < edge < face in mm.
unc_v = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
    f"'distance_accuracy_value','vertex_tol')"
)
unc_e = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-5),#{lu.eid},"
    f"'distance_accuracy_value','edge_tol')"
)
unc_f = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-4),#{lu.eid},"
    f"'distance_accuracy_value','face_tol')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_v.eid},#{unc_e.eid},#{unc_f.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx_mm','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
