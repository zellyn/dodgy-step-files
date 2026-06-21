"""N003 — Same-domain face merge inflates shared-vertex tolerance to worst input.

When two adjacent coplanar faces are merged, the resulting shared vertex inherits
a tolerance equal to the worst-case vertex among the merged inputs: 1.0E-1
instead of 2.0E-7 (from the other input vertex). Downstream algorithms then
treat points as fuzzy-equal where they were previously precise.

Two EDGE_CURVEs represent the edges from the two merged faces. Two
UNCERTAINTY_MEASURE_WITH_UNIT encode the before/after tolerances.

Byte assertions:
  contains(b'2.0E-7') and contains(b'1.0E-1')
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 2
  count_entity_def(b'EDGE_CURVE') == 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N003",
    defect=(
        "same-domain face merge: shared vertex inherits worst-input tol 1.0E-1 "
        "instead of 2.0E-7; two UNCERTAINTY_MEASURE_WITH_UNIT; two EDGE_CURVEs; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Two coplanar edges from two merged faces, sharing a vertex at x=10.
# Edge A: (0,0,0) -> (10,0,0)  (from face 1 — precise vertex, 2e-7 tol)
# Edge B: (10,0,0) -> (20,0,0) (from face 2 — imprecise vertex, 1e-1 tol)
pa0 = f.cartesian_point((0.0, 0.0, 0.0), name="pa0")
pa1 = f.cartesian_point((10.0, 0.0, 0.0), name="pa1_shared")
pb1 = f.cartesian_point((20.0, 0.0, 0.0), name="pb1")

va0 = f.vertex_point(pa0, name="va0_precise")
va1 = f.vertex_point(pa1, name="va1_shared_worst_tol")
vb1 = f.vertex_point(pb1, name="vb1")

da = f.direction((1.0, 0.0, 0.0))
veca = f.vector(da, 10.0)
la = f.line(pa0, veca)
eA = f.edge_curve(va0, va1, la, name="eA_face1")

db = f.direction((1.0, 0.0, 0.0))
vecb = f.vector(db, 10.0)
lb = f.line(pa1, vecb)
eB = f.edge_curve(va1, vb1, lb, name="eB_face2")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('merged',(#{eA.eid},#{eB.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N003','N003','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# Two UNCERTAINTY_MEASURE_WITH_UNIT: precise input (2.0E-7) and worst input (1.0E-1).
unc_precise = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(2.0E-7),#{lu.eid},"
    f"'distance_accuracy_value','pre_merge_precise_vertex_tol')"
)
unc_worst = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-1),#{lu.eid},"
    f"'distance_accuracy_value','merge_adopted_worst_vertex_tol')"
)

ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_precise.eid},#{unc_worst.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
