"""N155 — ShapeAnalysis_CheckSmallFace.CheckPin.tolerance-fallback.

CheckPin falls back to a default tolerance (1e-4) when myPrecision < 0
(invalid). Negative precision causes undefined comparison in sharpness tests.
Fixture documents the CheckPin candidate shape (pin face with documentary
UNCERTAINTY_MEASURE entries); negative-precision call must be made at runtime
via ShapeAnalysis_CheckSmallFace::SetPrecision(-1.0).

(No byte assertions; kernel-test-pair — defect requires SetPrecision(-1.0)
runtime invocation.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N155",
    defect=(
        "CheckPin tolerance-fallback: pin-face shape; SetPrecision(-1.0) "
        "triggers default 1e-4 fallback; negative myPrecision causes "
        "undefined sharpness comparison; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Pin-like geometry: thin vertical edge (height >> width).
p_bot = f.cartesian_point((0.0, 0.0, 0.0), name="p_bot")
p_top = f.cartesian_point((0.0, 0.0, 10.0), name="p_top")  # tall pin
p_side = f.cartesian_point((0.001, 0.0, 5.0), name="p_side_pin")  # narrow

v_bot = f.vertex_point(p_bot, name="v_bot")
v_top = f.vertex_point(p_top, name="v_top")
v_side = f.vertex_point(p_side, name="v_side")

d_z = f.direction((0.0, 0.0, 1.0))
e_pin = f.edge_curve(v_bot, v_top, f.line(p_bot, f.vector(d_z, 10.0)), name="e_pin")

# Tiny width edge for "pin" geometry.
d_x = f.direction((1.0, 0.0, 0.0))
e_width = f.edge_curve(v_bot, v_side, f.line(p_bot, f.vector(d_x, 0.001)), name="e_width")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('pin_face',(#{e_pin.eid},#{e_width.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N155','N155','',(#{prod_ctx.eid}))")
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
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-4),#{lu.eid},"
    f"'distance_accuracy_value','checkpin_fallback_tol')"
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
