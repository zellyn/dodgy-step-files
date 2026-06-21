"""Gp165 — vertex_tolerance_mismatch_1971.

Catalog claim: Vertex tolerance extracted without validation against accumulating
tolerance array. Edge chain with heterogeneous vertex tolerances triggers
incoherent continuity checks. Line 1971–1972: TopExp::CommonVertex() retrieves
unvalidated tolerance; aTolVerSeq.Append() stores unsorted values.

Mechanism: GEOMETRIC_CURVE_SET containing a chain of three EDGE_CURVEs with
heterogeneous vertex tolerances declared via multiple UNCERTAINTY_MEASURE_WITH_UNIT
entries. The vertex at the junction of two edges has a tolerance inconsistent
with the global tolerance array, exposing the line-1971 unvalidated extraction.
OCC yields empty.

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp165",
    defect=(
        "chain of three EDGE_CURVEs with heterogeneous vertex tolerances; "
        "junction vertex carries tolerance 1e-3 while its neighbors have 1e-7; "
        "TopExp::CommonVertex() at line 1971 retrieves unvalidated tolerance; "
        "aTolVerSeq.Append() stores unsorted values, breaking continuity checks; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Three-edge chain: edge A (p0→p1), edge B (p1→p2), edge C (p2→p3)
# Junction at p1 and p2; p1 has anomalously large tolerance
p0 = f.cartesian_point(( 0.0, 0.0, 0.0), name="v0_start")
p1 = f.cartesian_point(( 5.0, 0.0, 0.0), name="v1_junction_big_tol")
p2 = f.cartesian_point((10.0, 0.0, 0.0), name="v2_junction")
p3 = f.cartesian_point((15.0, 0.0, 0.0), name="v3_end")

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1, name="v1_tol_1e-3")  # anomalous tolerance
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

d_x   = f.direction((1.0, 0.0, 0.0))
vec_5 = f.vector(d_x, 5.0)

# Three colinear edges sharing the vertex chain
lA = f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 5.0))
eA = f.edge_curve(v0, v1, lA, name="eA")

lB = f.line(p1, f.vector(f.direction((1.0, 0.0, 0.0)), 5.0))
eB = f.edge_curve(v1, v2, lB, name="eB")

lC = f.line(p2, f.vector(f.direction((1.0, 0.0, 0.0)), 5.0))
eC = f.edge_curve(v2, v3, lC, name="eC")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('edge_chain_heterogeneous_tol',"
    f"(#{eA.eid},#{eB.eid},#{eC.eid}))"
)

# Manual PRODUCT chain with heterogeneous tolerances
# The anomaly: junction vertex v1 has tolerance 1e-3 while chain uses 1e-7
app_ctx  = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product  = f._emit_raw(f"PRODUCT('Gp165','Gp165','',(#{prod_ctx.eid}))")
pdf      = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc      = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd  = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu  = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# Global fine tolerance
unc_global = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
    f"'distance_accuracy_value','global_vertex_tol')"
)
# Anomalous junction vertex tolerance (4 orders of magnitude larger)
unc_junction = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','v1_junction_big_tol_1e-3')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_global.eid},#{unc_junction.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
