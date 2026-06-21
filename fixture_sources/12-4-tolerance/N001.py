"""N001 — Vertex UNCERTAINTY_MEASURE_WITH_UNIT larger than edge/face value (tolerance hierarchy violation).

After a healing pass, vertex tolerance (1.0E-2) is larger than edge tolerance
(1.0E-3), and edge tolerance is larger than face tolerance (1.0E-7). The
invariant that a vertex's tolerance disc must fit inside its edge's disc, and
an edge's disc inside its face's, is broken.

STEP encodes this via three UNCERTAINTY_MEASURE_WITH_UNIT instances (one per
level: face=1.0E-7, edge=1.0E-3, vertex=1.0E-2) in the
GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT. Downstream Boolean and meshing algorithms
rely on the hierarchy and produce incorrect results when violated.

Byte assertions:
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 3
  contains(b'1.0E-7') and contains(b'1.0E-3') and contains(b'1.0E-2')
  contains(b'GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N001",
    defect=(
        "tolerance hierarchy inverted: vertex tol=1.0E-2 > edge tol=1.0E-3 > "
        "face tol=1.0E-7; three UNCERTAINTY_MEASURE_WITH_UNIT in "
        "GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT; GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# A single edge: vertex at (0,0,0) -> (10,0,0)
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((10.0, 0.0, 0.0), name="p1")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 10.0)
line = f.line(p0, vec)
edge = f.edge_curve(v0, v1, line, name="edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('edges',(#{edge.eid}))")

# Product context
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N001','N001','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# Three tolerance levels — hierarchy inverted (face=1e-7, edge=1e-3, vertex=1e-2).
unc_face = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
    f"'face_distance_accuracy','face_tol_tight')"
)
unc_edge = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},"
    f"'edge_distance_accuracy','edge_tol_bloated')"
)
unc_vtx = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-2),#{lu.eid},"
    f"'vertex_distance_accuracy','vertex_tol_worst')"
)

# Three measures in GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT — the hierarchy violation.
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_face.eid},#{unc_edge.eid},#{unc_vtx.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
