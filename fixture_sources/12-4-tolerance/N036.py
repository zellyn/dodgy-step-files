"""N036 — Centroid validation breaks down when relative threshold goes below modeling tolerance.

Relative centroid threshold (deviation / model size) breaks down when the
bounding-box space diagonal is below ~20 mm at 0.02 mm model accuracy: a
0.1% threshold becomes smaller than the modeling tolerance, so even valid
round-trips fail validation. A tiny-model part has diagonal ~5 mm.

Byte assertions:
  contains(b'2.0E-2')
  count_entity_def(b'EDGE_CURVE') == 1
  contains(b'GEOMETRIC_REPRESENTATION_ITEM')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N036",
    defect=(
        "tiny model diagonal 5 mm; model accuracy 2.0E-2 mm; 0.1% relative "
        "centroid threshold = 0.005 mm < accuracy; valid round-trips fail; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Tiny model: edge 2 mm long (space diagonal ~2mm, within the <20mm problem zone).
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((2.0, 0.0, 0.0), name="p1_2mm")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 2.0)
line = f.line(p0, vec, name="tiny_model_edge")
edge = f.edge_curve(v0, v1, line, name="edge")

# GEOMETRIC_REPRESENTATION_ITEM — byte assertion value.
# Wrap the edge in a GEOMETRIC_REPRESENTATION_ITEM context.
gri = f._emit_raw(
    f"GEOMETRIC_REPRESENTATION_ITEM()"
)
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('tiny_model',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N036','N036','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Model accuracy 2.0E-2 mm — byte assertion; 0.1% of 2mm diagonal = 0.002 < this.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(2.0E-2),#{lu.eid},"
    f"'distance_accuracy_value','tiny_model_accuracy')"
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
