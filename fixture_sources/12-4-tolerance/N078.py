"""N078 — ShapeFix_Edge.FixSameParameter precision-floor.

FixSameParameter's interior tolerance computation uses hard-coded floors
(1e-7 to 1e-6 mm). When an edge declares tolerance tighter than the floor
(1e-15 or 1e-16 mm), the algorithm clamps to the floor, hiding the original
spec. SameParameter checks then pass incorrectly using the clamped tolerance.

Geometry: single edge (LINE 0→(1,0,0)) with ultra-tight UNCERTAINTY_MEASURE
(1e-15 mm) and edge-specific context tolerance (1e-16 mm).

(No byte assertions; kernel-test-pair — defect requires FixSameParameter
runtime invocation.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N078",
    defect=(
        "FixSameParameter precision-floor: edge (0,0,0)→(1,0,0); "
        "ultra-tight tolerance 1e-15 clamped to 1e-7 floor; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Single edge with ultra-tight declared tolerance.
p_start = f.cartesian_point((0.0, 0.0, 0.0), name="p_start")
p_end = f.cartesian_point((1.0, 0.0, 0.0), name="p_end")
v_start = f.vertex_point(p_start, name="v_start")
v_end = f.vertex_point(p_end, name="v_end")
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 1.0)
ln = f.line(p_start, vec, name="unit_line")
edge = f.edge_curve(v_start, v_end, ln, name="edge_ultra_tight")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('ultra_tight_tol',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N078','N078','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Ultra-tight 1e-15 tolerance — clamped to 1e-7 floor by FixSameParameter.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-15),#{lu.eid},"
    f"'distance_accuracy_value','ultra_tight_edge_tol')"
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
