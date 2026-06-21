"""Tb007 — NURBS knot-difference quantum below tolerance: knot collapses or doesn't.

A B_SPLINE_CURVE_WITH_KNOTS has knot vector (0.0, 1e-8, 1.0) with
multiplicities (4, 1, 4) for cubic. A receiver collapsing near-equal knots
within Precision::PConfusion (~1e-9) preserves the inner knot. A receiver
collapsing within Precision::Confusion (~1e-7) merges it into the leading knot,
raising leading multiplicity from 4 to 5 (degree+2) and degenerating the curve
start. Same input, different curves under different knot-equality policies.

Byte assertions:
  contains(b'B_SPLINE_CURVE_WITH_KNOTS')
  count_entity_def(b'CARTESIAN_POINT') == 5
  contains(b'1.0E-7')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb007",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS with inner knot at 1.0E-8 between "
        "Precision::PConfusion(~1e-9) and Precision::Confusion(~1e-7); "
        "knot collapses under loose policy, raising leading multiplicity to 5; "
        "OCC yields empty"
    ),
)

# Five control points for cubic B-spline. Byte assertion: exactly 5 CARTESIAN_POINTs.
cp0 = f.cartesian_point((0.0, 0.0, 0.0), name="cp0")
cp1 = f.cartesian_point((1.0, 1.0, 0.0), name="cp1")
cp2 = f.cartesian_point((2.0, 0.5, 0.0), name="cp2")
cp3 = f.cartesian_point((3.0, 1.0, 0.0), name="cp3")
cp4 = f.cartesian_point((4.0, 0.0, 0.0), name="cp4")

# Cubic B-spline with inner knot at 1.0E-8 (the time-bomb value).
# mults (4,1,4) sum to 9 = 5 poles + 3 degree + 1 — valid.
bsc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('knot_quantum_1e-8',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,4),(0.0,1.0E-8,1.0),.UNSPECIFIED.)"
)

vs = f.vertex_point(cp0, name="vstart")
ve = f.vertex_point(cp4, name="vend")
edge = f.edge_curve(vs, ve, bsc, name="e")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('cs',(#{edge.eid}))")

# Manual PRODUCT chain with declared tolerance 1.0E-7 (byte assertion).
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb007','Tb007','',(#{prod_ctx.eid}))")
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
    f"'distance_accuracy_value','tolerance_at_knot_quantum_boundary')"
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
