"""N029 — Inch-units silent treatment as mm (25.4x scale error).

A STEP file written in inches uses CONVERSION_BASED_UNIT to declare the inch
as 0.0254 m. An OpenCascade-based reader defaults to mm, treating the inch
values as millimetres: a 2-inch feature appears 50.8 mm in source but 2 mm in
target — 25.4x error.

Byte assertions:
  contains(b'CONVERSION_BASED_UNIT') or contains(b'.METRE.')
  matches(rb'0\\.0254')
  contains(b'EDGE_CURVE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N029",
    defect=(
        "inch units via CONVERSION_BASED_UNIT 0.0254 m; reader defaults to mm; "
        "50.8mm feature arrives as 2mm — 25.4x scale error; GEOMETRIC_CURVE_SET "
        "— OCC yields empty"
    ),
)

# Edge in inch units: 2 inches = 2 numeric units in the file.
# (Reader treating these as mm gives 2 mm; correct is 50.8 mm)
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((2.0, 0.0, 0.0), name="p1_2_inches")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 2.0)
line = f.line(p0, vec, name="two_inch_line")
edge = f.edge_curve(v0, v1, line, name="edge_2_inches")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('edges',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N029','N029','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

# Inch unit via CONVERSION_BASED_UNIT: 1 inch = 0.0254 m.
# SI_UNIT(.,$,.METRE.) is the base; CONVERSION_BASED_UNIT wraps it.
si_metre = f._emit_raw("SI_UNIT(.MILLI.,.METRE.)")
len_meas = f._emit_raw(f"LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.0254),#{si_metre.eid})")
# CONVERSION_BASED_UNIT: ('inch', 0.0254 m, LENGTH_UNIT)
inch_unit = f._emit_raw(
    f"(CONVERSION_BASED_UNIT('inch',#{len_meas.eid})LENGTH_UNIT()NAMED_UNIT(*))"
)
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{inch_unit.eid},"
    f"'distance_accuracy_value','inch_precision')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{inch_unit.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
