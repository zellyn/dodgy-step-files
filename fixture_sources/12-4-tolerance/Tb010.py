"""Tb010 — Self-intersection that vanishes when round-tripped through float32.

Quad boundary whose diagonals cross at sub-ULP separation in double precision.
Vertices at (0,0,0), (1.0000003,0,0), (2.0000007,0,0), (0.9999997,0.0000003,0)
form a near-degenerate crossing wire. After float32 round-trip the coordinates
collapse to (0,0,0), (1,0,0), (2,0,0), (1,0,0) — the crossing disappears because
two vertices become coincident. The "fix" was unintentional precision loss.

Byte assertions:
  count_entity_def(b'EDGE_CURVE') == 4
  count_entity_def(b'VERTEX_POINT') == 4
  contains(b'1.0E-7')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb010",
    defect=(
        "4 EDGE_CURVEs in self-crossing quad pattern; double-precision crossing "
        "vanishes after float32 round-trip (vertices collapse); "
        "declared 1.0E-7; GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Quad with self-crossing diagonal pattern in double precision.
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((1.0000003, 0.0, 0.0), name="p1_dbl_offset")
p2 = f.cartesian_point((2.0000007, 0.0, 0.0), name="p2")
p3 = f.cartesian_point((0.9999997, 0.0000003, 0.0), name="p3_almost_p1")

v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
v2 = f.vertex_point(p2, name="v2")
v3 = f.vertex_point(p3, name="v3_collapses_float32")

# Edge p0->p1
d01 = f.direction((1.0, 0.0, 0.0))
vec01 = f.vector(d01, 1.0000003)
l01 = f.line(p0, vec01)
e01 = f.edge_curve(v0, v1, l01, name="e01")

# Edge p1->p2
d12 = f.direction((1.0, 0.0, 0.0))
vec12 = f.vector(d12, 1.0000004)
l12 = f.line(p1, vec12)
e12 = f.edge_curve(v1, v2, l12, name="e12")

# Edge p2->p3 (the crossing diagonal direction)
import math
dx23 = 0.9999997 - 2.0000007
dy23 = 0.0000003 - 0.0
len23 = math.sqrt(dx23**2 + dy23**2)
d23 = f.direction((dx23/len23, dy23/len23, 0.0))
vec23 = f.vector(d23, len23)
l23 = f.line(p2, vec23)
e23 = f.edge_curve(v2, v3, l23, name="e23_crosses_diagonal")

# Edge p3->p0
dx30 = 0.0 - 0.9999997
dy30 = 0.0 - 0.0000003
len30 = math.sqrt(dx30**2 + dy30**2)
d30 = f.direction((dx30/len30, dy30/len30, 0.0))
vec30 = f.vector(d30, len30)
l30 = f.line(p3, vec30)
e30 = f.edge_curve(v3, v0, l30, name="e30")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('cs',(#{e01.eid},#{e12.eid},#{e23.eid},#{e30.eid}))"
)

# Manual PRODUCT chain with declared tolerance 1.0E-7.
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb010','Tb010','',(#{prod_ctx.eid}))")
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
    f"'distance_accuracy_value','double_precision_tolerance')"
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
