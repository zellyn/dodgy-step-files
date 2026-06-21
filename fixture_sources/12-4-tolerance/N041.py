"""N041 — Manifold epsilon-validity contract: cumulative transform error inflates epsilon.

Manifold tracks ε (max vertex perturbation to make mesh non-overlapping).
Cumulative transform/Boolean error inflates ε beyond input scale. Encoded as
4 EDGE_CURVEs: two pairs forming two tiny loops where inter-pair gap = 4.2E-3
(the inflated ε) while declared model tolerance is 1.0E-7 (the input scale).

Byte assertions:
  count_entity_def(b'EDGE_CURVE') == 4
  contains(b'1.0E-7') and contains(b'4.2E-3')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N041",
    defect=(
        "Manifold epsilon: input tol 1.0E-7; post-Boolean inflated epsilon 4.2E-3; "
        "4 EDGE_CURVEs; inter-pair gap = inflated epsilon; Boolean becomes unstable; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Pair A: two edges forming a tiny closed-ish loop at origin.
pa0 = f.cartesian_point((0.0, 0.0, 0.0), name="pa0")
pa1 = f.cartesian_point((1.0, 0.0, 0.0), name="pa1")
pa2 = f.cartesian_point((0.5, 1.0, 0.0), name="pa2")
va0 = f.vertex_point(pa0, name="va0")
va1 = f.vertex_point(pa1, name="va1")
va2 = f.vertex_point(pa2, name="va2")

da1 = f.direction((1.0, 0.0, 0.0))
veca1 = f.vector(da1, 1.0)
la1 = f.line(pa0, veca1)
eA1 = f.edge_curve(va0, va1, la1, name="eA1")

da2 = f.direction((-0.5, 1.0, 0.0))
veca2 = f.vector(da2, 1.118)
la2 = f.line(pa1, veca2)
eA2 = f.edge_curve(va1, va2, la2, name="eA2")

# Pair B: two more edges, displaced by 4.2E-3 (inflated epsilon) from pair A.
pb0 = f.cartesian_point((4.2E-3, 0.0, 0.0), name="pb0_eps_offset")
pb1 = f.cartesian_point((1.0 + 4.2E-3, 0.0, 0.0), name="pb1")
pb2 = f.cartesian_point((0.5 + 4.2E-3, 1.0, 0.0), name="pb2")
vb0 = f.vertex_point(pb0, name="vb0")
vb1 = f.vertex_point(pb1, name="vb1")
vb2 = f.vertex_point(pb2, name="vb2")

db1 = f.direction((1.0, 0.0, 0.0))
vecb1 = f.vector(db1, 1.0)
lb1 = f.line(pb0, vecb1)
eB1 = f.edge_curve(vb0, vb1, lb1, name="eB1")

db2 = f.direction((-0.5, 1.0, 0.0))
vecb2 = f.vector(db2, 1.118)
lb2 = f.line(pb1, vecb2)
eB2 = f.edge_curve(vb1, vb2, lb2, name="eB2")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('manifold_eps',(#{eA1.eid},#{eA2.eid},#{eB1.eid},#{eB2.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N041','N041','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Declared 1.0E-7 (input scale); inflated 4.2E-3 is the defect signal.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
    f"'distance_accuracy_value','input_model_precision')"
)
# Second measure to encode the inflated epsilon.
unc2 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(4.2E-3),#{lu.eid},"
    f"'distance_accuracy_value','post_boolean_inflated_epsilon')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid},#{unc2.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
