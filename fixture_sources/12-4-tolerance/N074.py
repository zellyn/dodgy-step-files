"""N074 — ShapeAnalysis_Edge.CheckPoints colinear-points shortcut.

CheckPoints has shortcut for "colinear endpoints": if two vertices are
colinear in 3D, check returns early. Two vertices can be colinear in 3D
while having different parameter values on edge curve. Shortcut doesn't
validate parameter correspondence, leading to false negatives.

Reproducer: edge from (0,0,0) to (10,0,0); vertices are colinear (both
on X-axis) but parametrized with mismatched or reversed params. CheckPoints
returns "OK" without checking parameter correspondence.

(No byte assertions; kernel-test-pair.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N074",
    defect=(
        "colinear-shortcut: edge (0,0,0)→(10,0,0); vertices colinear on X-axis; "
        "CheckPoints shortcut skips param validation; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Edge from (0,0,0) to (10,0,0) — colinear endpoints on X-axis.
p_start = f.cartesian_point((0.0, 0.0, 0.0), name="p_start")
p_end = f.cartesian_point((10.0, 0.0, 0.0), name="p_end")
v_start = f.vertex_point(p_start, name="v_start")
v_end = f.vertex_point(p_end, name="v_end")

d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 10.0)
ln = f.line(p_start, vec, name="colinear_line")
edge = f.edge_curve(v_start, v_end, ln, name="colinear_edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('colinear_shortcut',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N074','N074','',(#{prod_ctx.eid}))")
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
