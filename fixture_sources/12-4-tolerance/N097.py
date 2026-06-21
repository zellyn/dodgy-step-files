"""N097 — ShapeFix_ShapeTolerance.LimitTolerance same-min-and-max.

Call LimitTolerance(shape, 0.001, 0.001) with tmin == tmax. Condition
`iamax = (tmax >= tmin)` is true, but semantic intent of "clamp to [tmin,tmax]"
breaks when bounds are identical; treated as no-op.

Geometry: four-edge square face with mixed tolerances (5e-4, 0.002, 0.0015,
1e-5, 5e-3). LimitTolerance(shape, 0.001, 0.001, TopAbs_ALL) should normalize
all tolerances to 0.001 but leaves them unchanged.

(No byte assertions; kernel-test-pair — defect requires LimitTolerance runtime
invocation with tmin == tmax == 0.001.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N097",
    defect=(
        "LimitTolerance same-min-and-max: quad face with mixed tolerances; "
        "tmin==tmax==0.001 treated as no-op; all tolerances left unchanged; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Four-edge square (1×1) with distinct vertex tolerances.
pts = [
    f.cartesian_point((0.0, 0.0, 0.0), name="p0"),
    f.cartesian_point((1.0, 0.0, 0.0), name="p1"),
    f.cartesian_point((1.0, 1.0, 0.0), name="p2"),
    f.cartesian_point((0.0, 1.0, 0.0), name="p3"),
]
verts = [f.vertex_point(p) for p in pts]
dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
edges = []
for i in range(4):
    j = (i + 1) % 4
    d = f.direction((float(dirs[i][0]), float(dirs[i][1]), 0.0))
    vec = f.vector(d, 1.0)
    ln = f.line(pts[i], vec)
    edges.append(f.edge_curve(verts[i], verts[j], ln, name=f"e{i}"))

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('quad',(#{edges[0].eid},#{edges[1].eid},#{edges[2].eid},#{edges[3].eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N097','N097','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Mixed tolerances representing the quad's diversity.
unc1 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(5.0E-4),#{lu.eid},"
    f"'distance_accuracy_value','tol_v0')"
)
unc2 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(2.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','tol_v1')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc1.eid},#{unc2.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
