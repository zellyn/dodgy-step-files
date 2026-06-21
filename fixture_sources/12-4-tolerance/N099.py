"""N099 — BRepLib.UpdateEdgeTol multi-face-edge buffer overflow.

Edge shared by 6+ faces; UpdateEdgeTol samples face-edge intersections in a
loop with hardcoded buffer (space for ≤4 faces). Count of 6 overflows array,
causing memory corruption or silent data loss.

Geometry: central edge shared by 6 line segments emanating from origin — a
star-burst pattern providing the edge with 6 fan faces in the kernel context.

(No byte assertions; kernel-test-pair — defect requires UpdateEdgeTol runtime
invocation on star-burst edge topology.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="N099",
    defect=(
        "UpdateEdgeTol multi-face-edge buffer overflow: central edge shared by 6 faces; "
        "hardcoded 4-face buffer overflows on 6th face sample; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Central edge: (0,0,0) → (1,0,0)
p_center = f.cartesian_point((0.0, 0.0, 0.0), name="p_center")
p_end = f.cartesian_point((1.0, 0.0, 0.0), name="p_end")
v_center = f.vertex_point(p_center, name="v_center")
v_end = f.vertex_point(p_end, name="v_end")
d_x = f.direction((1.0, 0.0, 0.0))
central_edge = f.edge_curve(v_center, v_end, f.line(p_center, f.vector(d_x, 1.0)), name="central_edge")

# 6 fan edges from center, each 30° apart in XY plane.
fan_edges = []
for k in range(6):
    angle = k * math.pi / 3
    px = math.cos(angle)
    py = math.sin(angle)
    p_fan = f.cartesian_point((px, py, 0.0), name=f"p_fan{k}")
    v_fan = f.vertex_point(p_fan, name=f"v_fan{k}")
    d_fan = f.direction((px, py, 0.0))
    vec_fan = f.vector(d_fan, 1.0)
    ln_fan = f.line(p_center, vec_fan, name=f"ln_fan{k}")
    fan_edges.append(f.edge_curve(v_center, v_fan, ln_fan, name=f"fan_edge{k}"))

all_edges = [central_edge] + fan_edges
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('starburst',({','.join('#' + str(e.eid) for e in all_edges)}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N099','N099','',(#{prod_ctx.eid}))")
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
