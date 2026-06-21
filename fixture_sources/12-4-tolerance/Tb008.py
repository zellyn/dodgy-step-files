"""Tb008 — NURBS knot-difference quantum scaled by parametric range.

Like Tb007 but the knot vector is (0.0, 1.0E-2, 1.0E6). The inner knot
1.0E-2 is "small" relative to the range 1.0E6 (relative ~1e-8) but "large"
in absolute terms. A receiver using absolute parametric tolerance keeps the
knot; a receiver using relative parametric tolerance (knot-spacing/range)
drops it. Producers that emit large parametric domains (from re-parameterization
or splice operations) hit this regularly.

Byte assertions:
  contains(b'B_SPLINE_CURVE_WITH_KNOTS')
  count_entity_def(b'CARTESIAN_POINT') == 5
  contains(b'1.0E-6')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb008",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS with knots (0.0,1.0E-2,1.0E6); inner knot "
        "1.0E-2 tiny relative to range 1.0E6 (~1e-8 relative) but large absolute; "
        "absolute vs relative knot-tolerance policies produce different curves; "
        "OCC yields empty"
    ),
)

# Five control points spread across parametric domain [0, 1.0E6].
# Byte assertion: exactly 5 CARTESIAN_POINTs.
cp0 = f.cartesian_point((0.0, 0.0, 0.0), name="cp0")
cp1 = f.cartesian_point((2.5e5, 1.0, 0.0), name="cp1")
cp2 = f.cartesian_point((5.0e5, 0.5, 0.0), name="cp2")
cp3 = f.cartesian_point((7.5e5, 1.0, 0.0), name="cp3")
cp4 = f.cartesian_point((1.0e6, 0.0, 0.0), name="cp4")

# Cubic B-spline with large parameter domain; inner knot 1.0E-2 << range 1.0E6.
bsc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('large_param_range',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,4),(0.0,1.0E-2,1.0E6),.UNSPECIFIED.)"
)

vs = f.vertex_point(cp0, name="vstart")
ve = f.vertex_point(cp4, name="vend")
edge = f.edge_curve(vs, ve, bsc, name="e")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('cs',(#{edge.eid}))")

# Manual PRODUCT chain with default tolerance 1.0E-6 (byte assertion).
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb008','Tb008','',(#{prod_ctx.eid}))")
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
    f"'distance_accuracy_value','default_tolerance')"
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
