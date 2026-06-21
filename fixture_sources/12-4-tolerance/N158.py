"""N158 — location_transform_in_tolerance_eval bypass.

SameParameterEdge tolerance computation ignores surface location placement;
edge on transformed surface (translate +100mm, rotate 45°) yields false
tolerance sans transform.

Geometry: edge on a surface with a complex location transform (translate
+100mm in X, rotate 45° around Z) — tolerance computed without applying
the transform yields incorrect result.

(No byte assertions; kernel-test-pair — defect requires SameParameterEdge
runtime invocation on transformed surface.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N158",
    defect=(
        "location_transform_in_tolerance_eval bypass: edge on surface "
        "translated +100mm, rotated 45 deg; tolerance computed sans transform; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Plane surface at origin, but the edge is placed at the transformed location.
# Edge at transformed position (100, 100, 0) — simulating +100mm translate + 45° rotate.
sqrt2_inv = 1.0 / math.sqrt(2.0)
p_orig = f.cartesian_point((100.0, 100.0, 0.0), name="p_transformed_orig")
p_end = f.cartesian_point((100.0 + sqrt2_inv, 100.0 + sqrt2_inv, 0.0), name="p_transformed_end")
v_orig = f.vertex_point(p_orig, name="v_transformed_orig")
v_end = f.vertex_point(p_end, name="v_transformed_end")

d = f.direction((sqrt2_inv, sqrt2_inv, 0.0))  # 45-degree direction
ln = f.line(p_orig, f.vector(d, 1.0), name="transformed_line")
edge = f.edge_curve(v_orig, v_end, ln, name="edge_on_transformed_surface")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('location_bypass',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N158','N158','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
    f"'distance_accuracy_value','model_precision')"
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
