"""N045 — Vertex tolerance under-checked: edge-internal intersection ignored.

Two edges forming a T-junction: edge A ends at vertex V; edge B passes through
V's tolerance ball but does not end at V. The intersection check filters out
the internal crossing because it lies inside the vertex tolerance ball (1.0E-3).
The defect is an undetected edge-interior intersection.

Byte assertions:
  count_entity_def(b'EDGE_CURVE') == 2
  contains(b'1.0E-3')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N045",
    defect=(
        "T-junction: edge A ends at V; edge B passes through V's 1.0E-3 tol ball "
        "but doesn't terminate there; wire-intersection check silently filters; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Vertex V at (5, 0, 0); edge A goes from (0,0,0) to (5,0,0).
pA0 = f.cartesian_point((0.0, 0.0, 0.0), name="pA0")
pV = f.cartesian_point((5.0, 0.0, 0.0), name="pV_junction")
vA0 = f.vertex_point(pA0, name="vA0")
vV = f.vertex_point(pV, name="vV_junction")

dA = f.direction((1.0, 0.0, 0.0))
vecA = f.vector(dA, 5.0)
lineA = f.line(pA0, vecA, name="lineA")
eA = f.edge_curve(vA0, vV, lineA, name="eA_ends_at_V")

# Edge B: goes from (5, -10, 0) to (5, 10, 0) — passes through V's tol ball.
# B's endpoint at (5,-10,0) is far from V; it crosses the X-axis at (5,0,0) = V.
pB0 = f.cartesian_point((5.0, -10.0, 0.0), name="pB0")
pB1 = f.cartesian_point((5.0, 10.0, 0.0), name="pB1")
vB0 = f.vertex_point(pB0, name="vB0")
vB1 = f.vertex_point(pB1, name="vB1")

dB = f.direction((0.0, 1.0, 0.0))
vecB = f.vector(dB, 20.0)
lineB = f.line(pB0, vecB, name="lineB_through_V_interior")
eB = f.edge_curve(vB0, vB1, lineB, name="eB_passes_through_V_tol_ball")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('T_junction',(#{eA.eid},#{eB.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N045','N045','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Vertex tolerance ball 1.0E-3 — byte assertion.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','vertex_tol_ball')"
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
