"""N039 — Healing pass over-eagerly inflates tolerances 1000x on sub-shapes.

A healing pass touches every sub-shape and inflates edge/vertex tolerances even
on those whose existing tolerance already covers the actual deviation. Two
UNCERTAINTY_MEASURE_WITH_UNIT: native 1.0E-6 mm precision and post-fix
over-bumped 1.0E-3 mm — a 1000x bump applied across the whole model.

Byte assertions:
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 2
  contains(b'1.0E-6') and contains(b'1.0E-3')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N039",
    defect=(
        "healing pass inflates all tolerances 1000x: native 1.0E-6 → post-fix "
        "1.0E-3; 2×UNCERTAINTY_MEASURE_WITH_UNIT in GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Two consecutive edges sharing a vertex — the healer's target.
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((10.0, 0.0, 0.0), name="p1_shared")
p2 = f.cartesian_point((20.0, 0.0, 0.0), name="p2")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1_shared")
v2 = f.vertex_point(p2, name="v2")

d1 = f.direction((1.0, 0.0, 0.0))
vec1 = f.vector(d1, 10.0)
l1 = f.line(p0, vec1)
eA = f.edge_curve(v0, v1, l1, name="eA")

d2 = f.direction((1.0, 0.0, 0.0))
vec2 = f.vector(d2, 10.0)
l2 = f.line(p1, vec2)
eB = f.edge_curve(v1, v2, l2, name="eB")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('heal_bloat',(#{eA.eid},#{eB.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N039','N039','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# Two UNCERTAINTY_MEASURE_WITH_UNIT: native and post-fix 1000x-bloated.
unc_native = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
    f"'distance_accuracy_value','native_precision')"
)
unc_postfix = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','post_heal_over_bumped_1000x')"
)

ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_native.eid},#{unc_postfix.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
