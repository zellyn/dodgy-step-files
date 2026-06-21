"""Tb015 — Sliver edge length at sqrt(tol) — under squared comparison or linear?

An edge has 3D length 1.0e-3 mm in a file with declared tolerance 1.0e-6.
A kernel comparing length < tol (1.0e-6) says "alive" (1.0e-3 > 1.0e-6).
A kernel comparing length < sqrt(tol) (~1.0e-3) says "right at threshold".
A kernel comparing length*length < tol (1.0e-6 vs 1.0e-6) says "exact tie".
Three reasonable kernels can disagree on whether this edge survives heal.

Byte assertions:
  contains(b'1.0E-6')
  count_entity_def(b'EDGE_CURVE') == 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb015",
    defect=(
        "EDGE_CURVE of length 1.0E-3 mm with declared tol 1.0E-6; "
        "sqrt(1.0E-6) ~= 1.0E-3 — right at threshold for squared comparison; "
        "linear/squared/sqrt policies disagree on edge survival; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Edge of length exactly 1.0e-3 mm.
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((1.0e-3, 0.0, 0.0), name="p1_at_1e-3")

v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1_short_edge_1e-3")

d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 1.0e-3)
line = f.line(p0, vec)
edge = f.edge_curve(v0, v1, line, name="e_at_sqrt_tol_threshold")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('cs',(#{edge.eid}))")

# Manual PRODUCT chain with declared tolerance 1.0E-6 (byte assertion).
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb015','Tb015','',(#{prod_ctx.eid}))")
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
    f"'distance_accuracy_value','tol_whose_sqrt_equals_edge_length')"
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
