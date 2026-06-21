"""N065 — ShapeFix_ShapeTolerance.LimitTolerance partial-tree application.

LimitTolerance called on a compound containing both a shell and a solid.
The recursion stops at the shell boundary without descending into the solid's
interior, leaving inner topological elements un-limited.

Geometry: two edges representing a shell triangle and a solid interior
embedded at offset, with high tolerance (1e-1) in context.

(No byte assertions; kernel-test-pair — defect requires LimitTolerance runtime
invocation on compound with compound_max=1e-4.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N065",
    defect=(
        "LimitTolerance: compound with shell + solid; recursion halts at shell "
        "boundary; solid interior left un-limited; high tol 1e-1 context; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Triangular shell: 3 edges at (0,0,0)/(1,0,0)/(0,1,0).
pA = f.cartesian_point((0.0, 0.0, 0.0), name="pA")
pB = f.cartesian_point((1.0, 0.0, 0.0), name="pB")
pC = f.cartesian_point((0.0, 1.0, 0.0), name="pC")
vA = f.vertex_point(pA, name="vA")
vB = f.vertex_point(pB, name="vB")
vC = f.vertex_point(pC, name="vC")

dAB = f.direction((1.0, 0.0, 0.0))
eAB = f.edge_curve(vA, vB, f.line(pA, f.vector(dAB, 1.0)), name="eAB")
dBC = f.direction((-1.0, 1.0, 0.0))
eBC = f.edge_curve(vB, vC, f.line(pB, f.vector(dBC, 1.0)), name="eBC")
dCA = f.direction((0.0, -1.0, 0.0))
eCA = f.edge_curve(vC, vA, f.line(pC, f.vector(dCA, 1.0)), name="eCA")

# "Solid interior" edge at (5,5,5).
pD = f.cartesian_point((5.0, 5.0, 5.0), name="pD")
pE = f.cartesian_point((6.0, 5.0, 5.0), name="pE")
vD = f.vertex_point(pD, name="vD")
vE = f.vertex_point(pE, name="vE")
dDE = f.direction((1.0, 0.0, 0.0))
eDE = f.edge_curve(vD, vE, f.line(pD, f.vector(dDE, 1.0)), name="eDE_solid_interior")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('compound',(#{eAB.eid},#{eBC.eid},#{eCA.eid},#{eDE.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N065','N065','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# High tolerance 1e-1 — LimitTolerance(compound, max=1e-4) should limit all.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-1),#{lu.eid},"
    f"'distance_accuracy_value','coarse_tol')"
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
