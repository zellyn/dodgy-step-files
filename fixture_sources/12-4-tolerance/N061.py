"""N061 — BRepLib.BoundingVertex bounding-sphere under-estimate.

BRepLib's bounding sphere computation uses center-of-mass + max-distance
heuristic. With 4+ co-located vertices clustered within 1e-8, the heuristic
fails to produce a radius large enough to contain all points, resulting in
under-estimated bounding boxes downstream.

Byte assertions:
  count_entity_def(b'VERTEX_POINT') >= 5
  contains(b'1.0E-7')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N061",
    defect=(
        "5 vertices co-located within 1e-8 of (1,1,1); 4 degenerate edges; "
        "bounding-sphere heuristic under-estimates radius; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# 5 vertices clustered within 1e-8 of (1, 1, 1)
base = (1.0, 1.0, 1.0)
offsets = [
    (0.0, 0.0, 0.0),
    (5e-9, 0.0, 0.0),
    (0.0, 5e-9, 0.0),
    (0.0, 0.0, 5e-9),
    (5e-9, 5e-9, 5e-9),
]
pts = [
    f.cartesian_point(
        (base[0] + o[0], base[1] + o[1], base[2] + o[2]),
        name=f"p_clust{i}"
    )
    for i, o in enumerate(offsets)
]
verts = [f.vertex_point(pts[i], name=f"v_clust{i}") for i in range(5)]

# 4 degenerate edges connecting consecutive cluster vertices.
edges = []
for i in range(4):
    d = f.direction((1.0, 0.0, 0.0))
    vec = f.vector(d, 5e-9)
    ln = f.line(pts[i], vec, name=f"tiny_line{i}")
    edges.append(f.edge_curve(verts[i], verts[i + 1], ln, name=f"tiny_edge{i}"))

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('bounding_cluster',({','.join('#' + str(e.eid) for e in edges)}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N061','N061','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Receiver tolerance 1e-7 — cluster radius 5e-9 < this.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
    f"'distance_accuracy_value','receiver_tol')"
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
