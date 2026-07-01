"""Gp165 — vertex_tolerance_mismatch_1971.

Catalog claim: Vertex tolerance extracted without validation against accumulating
tolerance array. Edge chain with heterogeneous vertex tolerances triggers
incoherent continuity checks. Line 1971–1972: TopExp::CommonVertex() retrieves
unvalidated tolerance; aTolVerSeq.Append() stores unsorted values.

Mechanism: Three EDGE_CURVEs forming the bottom boundary of a 15x1 planar
ADVANCED_FACE (Z=0 plane). The vertex at the junction of the first two edges
has a tolerance declared 4 orders of magnitude larger than the global tolerance
(1e-3 vs 1e-7), exposing the line-1971 unvalidated tolerance extraction.

The defect edges are wired INTO the face boundary (not orphaned) so that
byte-level mutations to their geometry change the shape's tier-3 fingerprint.
The two UNCERTAINTY_MEASURE_WITH_UNIT entries carry the heterogeneous tolerance
claim: global 1e-7 and anomalous junction vertex 1e-3.

OCC heals the tolerance mismatch and loads the shape; Expected: shape(1).
The defect is demonstrated by the presence of both tolerance levels in context
and the junction vertex v1 participating in the face boundary.

Tier-3: n_faces_total == 1
Tier-3: face[0].surface_type == "plane"
Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp165",
    defect=(
        "PLANE Z=0; 15x1 ADVANCED_FACE; bottom boundary has three EDGE_CURVEs "
        "sharing junction vertex v1 at (5,0,0); global tolerance 1e-7, "
        "junction v1 tolerance 1e-3 (4 orders of magnitude larger); "
        "two UNCERTAINTY_MEASURE_WITH_UNIT in GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT; "
        "TopExp::CommonVertex() at line 1971 retrieves unvalidated junction tolerance; "
        "aTolVerSeq.Append() stores unsorted values, breaking continuity checks; "
        "OCC heals — shape(1)"
    ),
)

# Host: Z=0 plane (15 units wide, 1 unit tall)
p_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir   = f.direction((0.0, 0.0, 1.0))
xdir   = f.direction((1.0, 0.0, 0.0))
plc    = f.axis2_placement_3d(p_orig, zdir, xdir)
surf   = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Vertices — bottom row (the defect chain) + top row (clean return)
p_bl = f.cartesian_point(( 0.0, 0.0, 0.0), name="v0_start")
p_j1 = f.cartesian_point(( 5.0, 0.0, 0.0), name="v1_junction_big_tol")   # anomalous tol
p_j2 = f.cartesian_point((10.0, 0.0, 0.0), name="v2_junction")
p_br = f.cartesian_point((15.0, 0.0, 0.0), name="v3_end")
p_tr = f.cartesian_point((15.0, 1.0, 0.0), name="v_tr")
p_tl = f.cartesian_point(( 0.0, 1.0, 0.0), name="v_tl")

v_bl = f.vertex_point(p_bl)
v_j1 = f.vertex_point(p_j1, name="v1_tol_1e-3")   # junction with anomalous tolerance
v_j2 = f.vertex_point(p_j2)
v_br = f.vertex_point(p_br)
v_tr = f.vertex_point(p_tr)
v_tl = f.vertex_point(p_tl)

def mk_line_edge(vs, ve, p3_coords, dx, length, p2_coords, du):
    """Create an EDGE_CURVE with a LINE 3D curve and matching pcurve LINE."""
    p3e = f.cartesian_point(p3_coords)
    d3e = f.direction((dx, 0.0, 0.0) if dx > 0 else (-1.0, 0.0, 0.0))
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2_coords)
    d2e = f.direction((du, 0.0) if du > 0 else (-1.0, 0.0))
    v2  = f.vector(d2e, length)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pc',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# DEFECT: three-edge chain along the bottom boundary (eA, eB, eC)
# These share junction vertex v_j1 at (5,0,0) which has anomalous tolerance 1e-3.
eA = mk_line_edge(v_bl, v_j1,  ( 0.0, 0.0, 0.0), 1, 5.0,  ( 0.0, 0.0), 1)  # v0→v1
eB = mk_line_edge(v_j1, v_j2,  ( 5.0, 0.0, 0.0), 1, 5.0,  ( 5.0, 0.0), 1)  # v1→v2
eC = mk_line_edge(v_j2, v_br,  (10.0, 0.0, 0.0), 1, 5.0,  (10.0, 0.0), 1)  # v2→v3

# Clean cap and return edges (right cap, top return, left cap)
eR  = mk_line_edge(v_br, v_tr, (15.0, 0.0, 0.0), 0, 1.0,  (15.0, 0.0), 0)  # right cap (up)
eT  = mk_line_edge(v_tr, v_tl, (15.0, 1.0, 0.0), -1, 15.0, (15.0, 1.0), -1)  # top (left)
eL  = mk_line_edge(v_tl, v_bl, ( 0.0, 1.0, 0.0), 0, 1.0,  ( 0.0, 1.0), 0)  # left cap (down)

# Fix cap directions for the vertical edges
# eR goes up: +Y direction; eL goes down: -Y direction
# Let me redo cap edges with correct Y direction
def mk_vert_edge(vs, ve, p3_coords, dy, length, p2_coords, dv):
    p3e = f.cartesian_point(p3_coords)
    d3e = f.direction((0.0, float(dy), 0.0))
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2_coords)
    d2e = f.direction((0.0, float(dv)))
    v2  = f.vector(d2e, length)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pc',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

eR2 = mk_vert_edge(v_br, v_tr, (15.0, 0.0, 0.0), 1, 1.0, (15.0, 0.0), 1)
eL2 = mk_vert_edge(v_tl, v_bl,  (0.0, 1.0, 0.0), -1, 1.0,  (0.0, 1.0), -1)

loop = f.edge_loop([
    f.oriented_edge(eA,  True),   # v_bl → v_j1 (defect edge A)
    f.oriented_edge(eB,  True),   # v_j1 → v_j2 (defect edge B — junction)
    f.oriented_edge(eC,  True),   # v_j2 → v_br (defect edge C)
    f.oriented_edge(eR2, True),   # v_br → v_tr (right cap)
    f.oriented_edge(eT,  False),  # v_tl → v_tr reversed (top, goes left→right fwd, so rev=right→left)
    f.oriented_edge(eL2, True),   # v_tl → v_bl (left cap, down)
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])

# Product chain with TWO tolerance entries (the heterogeneous vertex tolerance claim):
#   - global fine tolerance 1.0E-7
#   - anomalous junction vertex tolerance 1.0E-3 (4 orders of magnitude larger)
# We emit the chain manually to include both UNCERTAINTY_MEASURE_WITH_UNIT entries.
block_start = max(9000, f._next_id)
f._next_id = block_start

app_ctx   = f._emit_raw("APPLICATION_CONTEXT('mechanical design')")
f.entities.insert(0, f.entities.pop())
prod_ctx  = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product   = f._emit_raw(f"PRODUCT('Gp165','Gp165','',({prod_ctx.ref()}))")
prod_form = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pd_ctx    = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
prod_def  = f._emit_raw(
    f"PRODUCT_DEFINITION('','',#{prod_form.eid},#{pd_ctx.eid})"
)
prod_shape = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{prod_def.eid})")
lu  = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# DEFECT: two UNCERTAINTY_MEASURE_WITH_UNIT — heterogeneous tolerances
unc_global = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
    f"'distance_accuracy_value','global_vertex_tol')"
)
unc_junction = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','v1_junction_big_tol_1e-3')"
)

grc = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT(({unc_global.ref()},{unc_junction.ref()}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT(({lu.ref()},{pau.ref()},{sau.ref()}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)
shape_rep = f._emit_raw(
    f"MANIFOLD_SURFACE_SHAPE_REPRESENTATION('',(#{sbsm.eid}),#{grc.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{prod_shape.eid},#{shape_rep.eid})")
