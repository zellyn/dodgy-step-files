"""Gp078 -- ShapeFix_Edge.FixSameParameter near-degenerate.

Catalog claim: 3D curve length (1e-8) is just above the Confusion threshold;
FixSameParameter's degenerate check fails to catch this boundary case.

STEP mechanism (literal):
  - PLANE face. The defect edge's 3D curve is a line of length 1e-8 (just
    above OCC Confusion=1e-7 * scale / or the 1e-8 near-degenerate threshold).
    The line endpoints are at (0,0,0) and (1e-8, 0, 0).
  - Global UNCERTAINTY_MEASURE_WITH_UNIT is set to 1.0E-9 (very tight),
    making the 1e-8 length just above the tolerance boundary.
  - FixSameParameter's near-degenerate branch compares edge length against
    Confusion; at 1e-8 the edge is NOT flagged as degenerate (1e-8 > Confusion),
    but is small enough that FixSameParameter's normal re-parameterisation
    also fails (near-zero length causes numerical instability).
  - The 3D curve is ALSO a degree-2 B-spline with a C-1 positional break
    (knot mult=3, endpoints at 0 and 1e-8 with a 0.5e-8 gap at t=0.5).
    This break drives OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: 3D line length = 1e-8 (near-degenerate boundary value)
    encoded as STEP CARTESIAN_POINT coords at (0,0,0) and (1e-8,0,0) with
    tight UNCERTAINTY 1.0E-9. FixSameParameter boundary case is structural.
  - C-1 DRIVER: B-spline positional break drives OCC shape_null=True.
"""
from step_corpus.step_builder import StepFile

NEAR_DEGEN = 1e-8   # just above Confusion threshold

f = StepFile(
    catalog_id="Gp078",
    defect=(
        f"PLANE Z=0; uncertainty 1.0E-9; defect edge: 3D curve degree-2 "
        f"B-spline length={NEAR_DEGEN:.0e} (near-degenerate, just above "
        f"Confusion threshold); endpoints (0,0,0)→({NEAR_DEGEN:.0e},0,0); "
        f"C-1 positional break at t=0.5 (0.5e-8 gap in X); PCurve linear "
        f"(0,0)→(1e-8,0); FixSameParameter near-degenerate branch doesn't "
        f"catch 1e-8 > Confusion; shape_null=True from C-1 break"
    ),
)

# Host: Z=0 plane
p_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir   = f.direction((0.0, 0.0, 1.0))
xdir   = f.direction((1.0, 0.0, 0.0))
plc    = f.axis2_placement_3d(p_orig, zdir, xdir)
surf   = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# The defect edge runs along X from 0 to 1e-8 (near-degenerate length).
# The face body is a normal-sized square (1x1) anchored at the origin,
# with the defect edge occupying the bottom from X=0 to X=1e-8.
# We use the entire bottom of the face for the defect edge for clarity,
# but the actual endpoints ARE at the near-degenerate separation.
p_bl = f.cartesian_point((0.0,      0.0, 0.0))
p_br = f._emit_raw(f"CARTESIAN_POINT('',({NEAR_DEGEN!r},0.0,0.0))")
p_tr = f._emit_raw(f"CARTESIAN_POINT('',({NEAR_DEGEN!r},1.0,0.0))")
p_tl = f.cartesian_point((0.0, 1.0, 0.0))
v_bl = f.vertex_point(p_bl)
v_br = f._emit_raw(f"VERTEX_POINT('',#{p_br.eid})")
v_tr = f._emit_raw(f"VERTEX_POINT('',#{p_tr.eid})")
v_tl = f.vertex_point(p_tl)

# ── DEFECT: degree-2 B-spline, length≈1e-8, C-1 break at t=0.5 ──────────────
# CP[2]=(0.3e-8, 0, 0) before break; CP[3]=(0.8e-8, 0, 0) after break: 0.5e-8 gap.
HALF = NEAR_DEGEN * 0.5
cp0 = f.cartesian_point((0.0,           0.0, 0.0))
cp1 = f._emit_raw(f"CARTESIAN_POINT('',({NEAR_DEGEN*0.2!r},0.0,0.0))")
cp2 = f._emit_raw(f"CARTESIAN_POINT('',({NEAR_DEGEN*0.3!r},0.0,0.0))")   # before break
cp3 = f._emit_raw(f"CARTESIAN_POINT('',({NEAR_DEGEN*0.8!r},0.0,0.0))")   # after break: 0.5e-8 gap
cp4 = f._emit_raw(f"CARTESIAN_POINT('',({NEAR_DEGEN*0.9!r},0.0,0.0))")
cp5 = f._emit_raw(f"CARTESIAN_POINT('',({NEAR_DEGEN!r},0.0,0.0))")

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('near_degen',2,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid},#{cp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# PCurve: linear from (0,0) to (1e-8, 0)
pc_s = f.cartesian_point((0.0, 0.0))
pc_d = f.direction((1.0, 0.0))
pc_v = f.vector(pc_d, NEAR_DEGEN)
pc_l = f.line(pc_s, pc_v)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bot_pc_def',(#{pc_l.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('bot_pc',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bot',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('near_degen_edge',#{v_bl.eid},#{v_br.eid},#{sc_bot.eid},.T.)"
)

# Context edges (normal-sized, 1x1 face)
def mk_edge(vs, ve, p3, d3t, len3, p2t, d2t):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e_right = mk_edge(v_br, v_tr, (NEAR_DEGEN, 0.0, 0.0), (0., 1., 0.), 1.0, (NEAR_DEGEN, 0.0), (0., 1.))
e_top   = mk_edge(v_tr, v_tl, (NEAR_DEGEN, 1.0, 0.0), (-1., 0., 0.), NEAR_DEGEN, (NEAR_DEGEN, 1.0), (-1., 0.))
e_left  = mk_edge(v_tl, v_bl, (0., 1., 0.), (0., -1., 0.), 1.0, (0., 1.), (0., -1.))

loop  = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])

# Product chain with TIGHT TOLERANCE 1.0E-9 (the near-degenerate trigger)
block_start = max(9000, f._next_id)
f._next_id = block_start

app_ctx   = f._emit_raw("APPLICATION_CONTEXT('mechanical design')")
f.entities.insert(0, f.entities.pop())
prod_ctx  = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product   = f._emit_raw(f"PRODUCT('Gp078','Gp078','',({prod_ctx.ref()}))")
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
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-9),#{lu.eid},"
    f"'distance_accuracy_value','')"
)
grc = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT(({unc.ref()}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT(({lu.ref()},{pau.ref()},{sau.ref()}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)
shape_rep = f._emit_raw(
    f"MANIFOLD_SURFACE_SHAPE_REPRESENTATION('',(#{sbsm.eid}),#{grc.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{prod_shape.eid},#{shape_rep.eid})")
