"""N063 — ShapeFix_Edge.FixVertexTolerance escalation cascade.

Multiple edges share a common vertex. FixVertexTolerance on edge A escalates
the vertex tolerance. When FixVertexTolerance is called on edge B (sharing the
same vertex), it sees the escalated value and re-escalates without re-checking
necessity, causing unbounded growth.

Byte assertions:
  count_entity_def(b'EDGE_CURVE') == 3
  contains(b'1.0E-5')
  contains(b'1.0E-4')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N063",
    defect=(
        "3-edge star: hub at origin; endpoints at (1,0,0),(0,1,0),(0,0,1); "
        "hub vertex tol 1e-5, edge tol 1e-4; FixVertexTolerance cascade escalates hub; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Hub vertex at origin.
p_hub = f.cartesian_point((0.0, 0.0, 0.0), name="p_hub")
v_hub = f.vertex_point(p_hub, name="v_hub")

# Three spoke endpoints.
p1 = f.cartesian_point((1.0, 0.0, 0.0), name="p_spoke1")
p2 = f.cartesian_point((0.0, 1.0, 0.0), name="p_spoke2")
p3 = f.cartesian_point((0.0, 0.0, 1.0), name="p_spoke3")
v1 = f.vertex_point(p1, name="v_spoke1")
v2 = f.vertex_point(p2, name="v_spoke2")
v3 = f.vertex_point(p3, name="v_spoke3")

# Edge A: hub → (1,0,0)
dA = f.direction((1.0, 0.0, 0.0))
vecA = f.vector(dA, 1.0)
lineA = f.line(p_hub, vecA, name="lineA")
eA = f.edge_curve(v_hub, v1, lineA, name="eA_spoke1")

# Edge B: hub → (0,1,0)
dB = f.direction((0.0, 1.0, 0.0))
vecB = f.vector(dB, 1.0)
lineB = f.line(p_hub, vecB, name="lineB")
eB = f.edge_curve(v_hub, v2, lineB, name="eB_spoke2")

# Edge C: hub → (0,0,1)
dC = f.direction((0.0, 0.0, 1.0))
vecC = f.vector(dC, 1.0)
lineC = f.line(p_hub, vecC, name="lineC")
eC = f.edge_curve(v_hub, v3, lineC, name="eC_spoke3")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('star_topo',(#{eA.eid},#{eB.eid},#{eC.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N063','N063','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Hub vertex tol 1e-5; edge tol 1e-4 — cascade escalates hub beyond edge tol.
unc_vtx = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-5),#{lu.eid},"
    f"'distance_accuracy_value','hub_vertex_tol')"
)
unc_edge = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-4),#{lu.eid},"
    f"'distance_accuracy_value','spoke_edge_tol')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_vtx.eid},#{unc_edge.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
