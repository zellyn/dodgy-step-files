"""Tb016 — Tolerance budget exhausted by accumulation across long edge chain.

A polyline of 5 short edges (length ~1.0e-3 mm each); each adjacent vertex pair
is offset by a constant 2.0e-7 mm in +y. Each individual gap is sub-tolerance
(declared 1.0e-6 mm), but cumulative drift end-to-end after 5 edges is 1.0e-6
mm = exactly the declared tolerance budget. Whether the wire closes depends on
whether the kernel sums residuals or only checks adjacent pairs.

Byte assertions:
  count_entity_def(b'EDGE_CURVE') == 5
  count_entity_def(b'VERTEX_POINT') == 6
  contains(b'1.0E-6')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb016",
    defect=(
        "5 EDGE_CURVEs, 6 VERTEX_POINTs; each adjacent vertex pair offset 2.0E-7 mm in +y; "
        "per-edge gap sub-tolerance (1.0E-6); cumulative drift after 5 edges = 1.0E-6 = tol; "
        "end-to-end closure depends on summing vs per-pair check; OCC yields empty"
    ),
)

# 5 edges, 6 vertices. Each vertex drifts 2.0E-7 mm in +y cumulatively.
pts = [
    f.cartesian_point((i * 1.0e-3, i * 2.0e-7, 0.0), name=f"p{i}")
    for i in range(6)
]
verts = [f.vertex_point(pts[i], name=f"v{i}") for i in range(6)]

# Shared direction +x (each edge runs ~1e-3 mm in +x).
dx = f.direction((1.0, 0.0, 0.0))
vec_seg = f.vector(dx, 1.0e-3)

edges = []
for i in range(5):
    line = f.line(pts[i], vec_seg, name=f"l{i}{i+1}")
    e = f.edge_curve(verts[i], verts[i+1], line, name=f"e{i}{i+1}")
    edges.append(e)

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('cs',({','.join('#'+str(e.eid) for e in edges)}))"
)

# Manual PRODUCT chain with declared tolerance 1.0E-6.
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb016','Tb016','',(#{prod_ctx.eid}))")
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
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
    f"'distance_accuracy_value','cumulative_drift_budget')"
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
