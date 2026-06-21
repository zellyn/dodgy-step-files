"""N043 — Shape-to-shape distance reports nonzero gap for clearly intersecting parts.

For two shapes that demonstrably intersect, the minimum-distance query returns
nonzero (6.3E-5 or 8.3E-2) instead of zero. The algorithm samples corner/edge
endpoints but doesn't verify true intersection. Three UNCERTAINTY_MEASURE_WITH_UNIT
instances encode the gap values and model precision.

Byte assertions:
  count_entity_def(b'CYLINDRICAL_SURFACE') == 1
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 3
  contains(b'6.3E-5') and contains(b'8.3E-2')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N043",
    defect=(
        "distance query: 1 CYLINDRICAL_SURFACE intersects main part but returns "
        "6.3E-5 or 8.3E-2 nonzero gap; 3×UNCERTAINTY_MEASURE_WITH_UNIT; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Cylinder: r=5 mm, axis Z — the "intersecting" part.
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0), name="cyl_orig")
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl',#{cyl_plc.eid},5.0)")

# A simple edge representing the main part geometry.
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((10.0, 0.0, 0.0), name="p1")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 10.0)
line = f.line(p0, vec)
edge = f.edge_curve(v0, v1, line, name="main_edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('dist_query',(#{cyl.eid},#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N043','N043','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# Three UNCERTAINTY_MEASURE_WITH_UNIT: model precision + two bogus gap values.
unc1 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
    f"'distance_accuracy_value','model_precision')"
)
unc2 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(6.3E-5),#{lu.eid},"
    f"'distance_accuracy_value','sampled_gap_type_A')"
)
unc3 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(8.3E-2),#{lu.eid},"
    f"'distance_accuracy_value','sampled_gap_type_B')"
)

ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc1.eid},#{unc2.eid},#{unc3.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
