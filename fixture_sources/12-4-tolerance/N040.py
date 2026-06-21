"""N040 — Limit Tolerance clamp re-exposes gaps that bloated tolerances were hiding.

Salome's Limit Tolerance forces tolerance back down. When tolerances were
inflated by upstream tools to hide real gaps, clamping back re-exposes them.
Two UNCERTAINTY_MEASURE_WITH_UNIT: bloated 1.0E-3 pre-clamp and tight 1.0E-6
post-clamp. Four VERTEX_POINTs: two consecutive edges with shared junction
vertices differing by ~5e-4 mm, hidden within the bloated tol but exposed
after clamping.

Byte assertions:
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 2
  contains(b'1.0E-3') and contains(b'1.0E-6')
  count_entity_def(b'VERTEX_POINT') == 4

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N040",
    defect=(
        "Limit Tolerance re-exposes gap: bloated tol 1.0E-3 hides 5.0E-4 gap; "
        "clamped to 1.0E-6 gap reappears; 4 VERTEX_POINTs with separate junctions; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Edge A: (0,0,0) -> (10,0,0)
pa0 = f.cartesian_point((0.0, 0.0, 0.0), name="pa0")
pa1 = f.cartesian_point((10.0, 0.0, 0.0), name="pa1_nominal")
# Edge B: starts at (10.0005,0,0) — 5e-4 gap hidden by bloated tol.
pb0 = f.cartesian_point((10.0005, 0.0, 0.0), name="pb0_hidden_gap")
pb1 = f.cartesian_point((20.0005, 0.0, 0.0), name="pb1")

va0 = f.vertex_point(pa0, name="va0")
va1 = f.vertex_point(pa1, name="va1_nominal")
vb0 = f.vertex_point(pb0, name="vb0_with_gap")
vb1 = f.vertex_point(pb1, name="vb1")

da = f.direction((1.0, 0.0, 0.0))
veca = f.vector(da, 10.0)
la = f.line(pa0, veca)
eA = f.edge_curve(va0, va1, la, name="eA")

db = f.direction((1.0, 0.0, 0.0))
vecb = f.vector(db, 10.0)
lb = f.line(pb0, vecb)
eB = f.edge_curve(vb0, vb1, lb, name="eB")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('clamp',(#{eA.eid},#{eB.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N040','N040','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# Two UNCERTAINTY_MEASURE_WITH_UNIT: bloated pre-clamp and tight post-clamp.
unc_bloated = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','pre_clamp_bloated_tol')"
)
unc_clamped = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
    f"'distance_accuracy_value','post_clamp_tight_tol')"
)

ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_bloated.eid},#{unc_clamped.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
