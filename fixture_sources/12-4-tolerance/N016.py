"""N016 — Edge tolerance 2-3 orders of magnitude > file tolerance (CATIA per-edge precision).

CATIA writes per-edge tolerance values that are 2-3 orders of magnitude larger
than the file's default tolerance. Receivers reading only the global tolerance
find gaps between adjacent faces and treat the body as an open shell.

Three UNCERTAINTY_MEASURE_WITH_UNIT instances encode:
- global file tolerance: 1.0E-4 mm
- per-edge tolerance (some edges): 5.0E-3 mm
- worst-case per-edge tolerance: 1.0E-2 mm

Byte assertions:
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 3
  contains(b'1.0E-4') and contains(b'1.0E-2') and contains(b'5.0E-3')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N016",
    defect=(
        "CATIA per-edge tol: global=1.0E-4, edge1=5.0E-3, edge2=1.0E-2; "
        "receiver using only global sees gaps; 3×UNCERTAINTY_MEASURE_WITH_UNIT; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Two edges from adjacent CATIA faces. Shared vertex at (10,0,0).
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((10.0, 0.0, 0.0), name="p1_shared")
p2 = f.cartesian_point((20.0, 0.0, 0.0), name="p2")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1_shared")
v2 = f.vertex_point(p2, name="v2")

d1 = f.direction((1.0, 0.0, 0.0))
vec1 = f.vector(d1, 10.0)
l1 = f.line(p0, vec1)
eA = f.edge_curve(v0, v1, l1, name="eA_tight")

d2 = f.direction((1.0, 0.0, 0.0))
vec2 = f.vector(d2, 10.0)
l2 = f.line(p1, vec2)
eB = f.edge_curve(v1, v2, l2, name="eB_loose")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('catia_edges',(#{eA.eid},#{eB.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N016','N016','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# Three UNCERTAINTY_MEASURE_WITH_UNIT: global and two per-edge levels.
unc_global = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-4),#{lu.eid},"
    f"'distance_accuracy_value','global_file_tolerance')"
)
unc_edge1 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(5.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','catia_per_edge_tol_medium')"
)
unc_edge2 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-2),#{lu.eid},"
    f"'distance_accuracy_value','catia_per_edge_tol_worst')"
)

ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_global.eid},#{unc_edge1.eid},#{unc_edge2.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
