"""N008 — Vertex tolerance inflation by repeated self-intersection healing cascades

A self-intersection-resolution pass modifies a pcurve and bumps the affected
vertex's tolerance to encompass both the original and the new position.
Successive rounds of this pass grow the vertex tolerance ball geometrically
(e.g. 1e-7 → 1e-3 in a few iterations), eventually masking real gaps in
modelled threads or fillets.

Reproducer: A closed-shell unit cube whose top face carries a small rectangular
inner-loop hole; the hole's outer wire is described by two near-tangent B-spline
edges that cross at a measurable distance (~2.5e-4) close to one shared vertex.
The two edges are not coincident in 3D -- they cross slightly inside
Precision::Confusion() scaled by file uncertainty, so
ShapeFix_Wire::FixSelfIntersection has something real to attempt and the recorded
UNCERTAINTY cascade (1.0e-7..1e-3) reflects the actual geometric inflation per pass.

Byte assertions:
  contains(b'vertex_tol_pass0_native')
  contains(b'vertex_tol_pass4_overrun')
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 5

Tier-3: n_edges_total >= 27
Tier-3: face[0].surface_type == "plane"
Tier-3: face[5].surface_type == "plane"
Expected: occt=shape(1)/shape(1) gmsh=shape(32) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N008",
    defect=(
        "CLOSED_SHELL cube; top face has inner wire with two near-tangent "
        "B_SPLINE_CURVE edges crossing at ~2.5e-4 mm; FixSelfIntersection "
        "cascades inflate vertex tolerance: 1e-7→1e-6→1e-5→1e-4→1e-3; "
        "five UNCERTAINTY_MEASURE_WITH_UNIT entries record the cascade growth"
    ),
)

# ── 8 cube corners ─────────────────────────────────────────────────────────
p000 = f.cartesian_point((0.0,   0.0,  0.0))
p100 = f.cartesian_point((10.0,  0.0,  0.0))
p110 = f.cartesian_point((10.0, 10.0,  0.0))
p010 = f.cartesian_point((0.0,  10.0,  0.0))
p001 = f.cartesian_point((0.0,   0.0, 10.0))
p101 = f.cartesian_point((10.0,  0.0, 10.0))
p111 = f.cartesian_point((10.0, 10.0, 10.0))
p011 = f.cartesian_point((0.0,  10.0, 10.0))

v000 = f.vertex_point(p000)
v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110)
v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001)
v101 = f.vertex_point(p101)
v111 = f.vertex_point(p111)
v011 = f.vertex_point(p011)

# ── Direction/vector library ─────────────────────────────────────────────
dpx = f.direction((1.0,  0.0, 0.0), name="+x")
dpy = f.direction((0.0,  1.0, 0.0), name="+y")
dpz = f.direction((0.0,  0.0, 1.0), name="+z")
dmx = f.direction((-1.0, 0.0, 0.0), name="-x")
dmy = f.direction((0.0, -1.0, 0.0), name="-y")

vx10 = f.vector(dpx, 10.0, name="vx10")
vy10 = f.vector(dpy, 10.0, name="vy10")
vz10 = f.vector(dpz, 10.0, name="vz10")

# ── Cube outer-loop straight edges ──────────────────────────────────────
# Bottom face edges (z=0)
e_b0 = f.edge_curve(v000, v100, f.line(p000, vx10), name="e_b0")
e_b1 = f.edge_curve(v100, v110, f.line(p100, vy10), name="e_b1")
e_b2 = f.edge_curve(v010, v110, f.line(p010, vx10), name="e_b2")
e_b3 = f.edge_curve(v000, v010, f.line(p000, vy10), name="e_b3")
# Top face edges (z=10)
e_t0 = f.edge_curve(v001, v101, f.line(p001, vx10), name="e_t0")
e_t1 = f.edge_curve(v101, v111, f.line(p101, vy10), name="e_t1")
e_t2 = f.edge_curve(v011, v111, f.line(p011, vx10), name="e_t2")
e_t3 = f.edge_curve(v001, v011, f.line(p001, vy10), name="e_t3")
# Vertical edges
e_v0 = f.edge_curve(v000, v001, f.line(p000, vz10), name="e_v0")
e_v1 = f.edge_curve(v100, v101, f.line(p100, vz10), name="e_v1")
e_v2 = f.edge_curve(v110, v111, f.line(p110, vz10), name="e_v2")
e_v3 = f.edge_curve(v010, v011, f.line(p010, vz10), name="e_v3")

# ── Cube planes (one per face) ───────────────────────────────────────────
plc_bot = f.axis2_placement_3d(p000, dmy, dpx, name="p_bot")
s_bot   = f.plane(plc_bot, name="s_bot")
plc_top = f.axis2_placement_3d(p001, dpz, dpx, name="p_top")
s_top   = f.plane(plc_top, name="s_top")
plc_x0  = f.axis2_placement_3d(p000, dmx, dpy, name="p_x0")
s_x0    = f.plane(plc_x0, name="s_x0")
plc_x1  = f.axis2_placement_3d(p100, dpx, dpy, name="p_x1")
s_x1    = f.plane(plc_x1, name="s_x1")
plc_y0  = f.axis2_placement_3d(p000, dmy, dpx, name="p_y0")
s_y0    = f.plane(plc_y0, name="s_y0")
plc_y1  = f.axis2_placement_3d(p010, dpy, dpx, name="p_y1")
s_y1    = f.plane(plc_y1, name="s_y1")

# ── Self-intersecting B-spline pcurve (the actual defect) ──────────────
# Two B-spline edges nominally meeting at vertex at (5.0, 5.0, 10.0)
# but whose interiors cross at ~2.5e-4 separation.
p_inner = f.cartesian_point((5.0, 5.0, 10.0), name="inner_v")
v_shared = f.vertex_point(p_inner, name="shared_v")

# Curve A: enters from +x side, dips slightly
cpA0 = f.cartesian_point((4.0,    4.999875, 10.0))
cpA1 = f.cartesian_point((4.5,    5.000000, 10.0))
cpA2 = f.cartesian_point((4.8,    4.999850, 10.0))
cpA3 = f.cartesian_point((5.0,    5.000000, 10.0))
curveA = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('curveA',3,"
    f"(#{cpA0.eid},#{cpA1.eid},#{cpA2.eid},#{cpA3.eid}),.UNSPECIFIED.,.F.,.F.,"
    f"(4,4),(0.0,1.0),.UNSPECIFIED.)"
)
vA_start = f.vertex_point(cpA0, name="A_start")
eA = f.edge_curve(vA_start, v_shared, curveA, name="selfint_A")

# Curve B: approaches from -x side, rises through the middle of curve A
cpB0 = f.cartesian_point((4.0,    5.000125, 10.0))
cpB1 = f.cartesian_point((4.5,    5.000000, 10.0))
cpB2 = f.cartesian_point((4.8,    5.000150, 10.0))
cpB3 = f.cartesian_point((5.0,    5.000000, 10.0))
curveB = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('curveB',3,"
    f"(#{cpB0.eid},#{cpB1.eid},#{cpB2.eid},#{cpB3.eid}),.UNSPECIFIED.,.F.,.F.,"
    f"(4,4),(0.0,1.0),.UNSPECIFIED.)"
)
vB_start = f.vertex_point(cpB0, name="B_start")
eB = f.edge_curve(vB_start, v_shared, curveB, name="selfint_B")

# Close the inner hole loop with a short straight edge
din1  = f.direction((0.0, 1.0, 0.0), name="inner_d1")
vin1  = f.vector(din1, 2.5e-4, name="inner_v1")
lin1  = f.line(cpA0, vin1, name="inner_l1")
e_close = f.edge_curve(vA_start, vB_start, lin1, name="inner_close")

# Inner hole loop on the top face
inner_loop = f.edge_loop([
    f.oriented_edge(eA, True),
    f.oriented_edge(eB, False),
    f.oriented_edge(e_close, False),
], name="inner_loop")
inner_bound = f._emit_raw(
    f"FACE_BOUND('inner_hole',#{inner_loop.eid},.F.)"
)

# ── Six face boundary loops & faces (closed shell) ───────────────────────
# Bottom face z=0
lbot = f.edge_loop([
    f.oriented_edge(e_b0, True),
    f.oriented_edge(e_b1, True),
    f.oriented_edge(e_b2, False),
    f.oriented_edge(e_b3, False),
])
fbot = f.advanced_face([f.face_outer_bound(lbot)], s_bot, name="bottom")

# Top face z=10 (with inner self-intersecting loop)
ltop_outer = f.edge_loop([
    f.oriented_edge(e_t0, True),
    f.oriented_edge(e_t1, True),
    f.oriented_edge(e_t2, False),
    f.oriented_edge(e_t3, False),
])
fob_top = f.face_outer_bound(ltop_outer)
ftop = f._emit_raw(
    f"ADVANCED_FACE('top_with_hole',(#{fob_top.eid},#{inner_bound.eid}),#{s_top.eid},.T.)"
)

# x0 face (x=0)
lx0 = f.edge_loop([
    f.oriented_edge(e_b3, True),
    f.oriented_edge(e_v3, True),
    f.oriented_edge(e_t3, False),
    f.oriented_edge(e_v0, False),
])
fx0 = f.advanced_face([f.face_outer_bound(lx0)], s_x0, name="x0")

# x1 face (x=10)
lx1 = f.edge_loop([
    f.oriented_edge(e_b1, True),
    f.oriented_edge(e_v2, True),
    f.oriented_edge(e_t1, False),
    f.oriented_edge(e_v1, False),
])
fx1 = f.advanced_face([f.face_outer_bound(lx1)], s_x1, name="x1")

# y0 face (y=0)
ly0 = f.edge_loop([
    f.oriented_edge(e_b0, True),
    f.oriented_edge(e_v1, True),
    f.oriented_edge(e_t0, False),
    f.oriented_edge(e_v0, False),
])
fy0 = f.advanced_face([f.face_outer_bound(ly0)], s_y0, name="y0")

# y1 face (y=10)
ly1 = f.edge_loop([
    f.oriented_edge(e_b2, True),
    f.oriented_edge(e_v2, True),
    f.oriented_edge(e_t2, False),
    f.oriented_edge(e_v3, False),
])
fy1 = f.advanced_face([f.face_outer_bound(ly1)], s_y1, name="y1")

# ── Closed shell + manifold solid ────────────────────────────────────────
shell = f.closed_shell([fbot, ftop, fx0, fx1, fy0, fy1], name="cube_shell")
msb   = f.manifold_solid_brep(shell, name="cube")

# ── Manual PRODUCT chain with uncertainty cascade (5 levels) ─────────────
# Use _emit_raw so all 5 UNCERTAINTY_MEASURE entries are preserved
app_ctx  = f._emit_raw("APPLICATION_CONTEXT('automotive design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product  = f._emit_raw(f"PRODUCT('N008','N008','',(#{prod_ctx.eid}))")
pdf      = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc      = f._emit_raw(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')")
pd       = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds      = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu  = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# Cascade growth at the shared vertex across successive FixSelfIntersection passes
unc0 = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},'distance_accuracy_value','vertex_tol_pass0_native')")
unc1 = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},'distance_accuracy_value','vertex_tol_pass1')")
unc2 = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-5),#{lu.eid},'distance_accuracy_value','vertex_tol_pass2')")
unc3 = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-4),#{lu.eid},'distance_accuracy_value','vertex_tol_pass3')")
unc4 = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},'distance_accuracy_value','vertex_tol_pass4_overrun')")

ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc0.eid},#{unc1.eid},#{unc2.eid},#{unc3.eid},#{unc4.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
shape_rep = f._emit_raw(
    f"ADVANCED_BREP_SHAPE_REPRESENTATION('',(#{msb.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{shape_rep.eid})")

f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N008.stp")
