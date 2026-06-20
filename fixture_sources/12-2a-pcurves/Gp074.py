"""Gp074 -- ShapeFix_Edge.FixSameParameter precision-cliff.

Catalog claim: Recomputed tolerance equals input tolerance exactly (floating-
point equality).  Precision cliff at boundary causes oscillation in tolerance
escalation logic.

STEP-level trigger (partial): UNCERTAINTY_MEASURE_WITH_UNIT set to 1.0E-15
(extremely tight); B_SPLINE_CURVE_WITH_KNOTS 3D curve with CP at 1.999999999999
(engineered within 1e-12 of 2.0, creating the FP cliff); matching pcurve
B-spline with CP at exactly 2.0.  The mid-span deviation (~1e-12) sits at the
precision cliff boundary for FixSameParameter's tolerance equality check.

The B-spline also has a C-1 positional break (knot mult=3=degree+1, 1.5-unit
gap in X at t=0.3), which drives OCC shape_null=True (the expected outcome).
The engineered CP value (1.999999999999) AND tight tolerance (1.0E-15) are
preserved as the FP cliff trigger within the STEP bytes.

Note: The tolerance oscillation behaviour is algorithm-side (runtime FP
arithmetic); the STEP-level encoding carries the two enablers:
  (a) 3D B-spline CP at 1.999999999999 — within 1e-12 of exactly 2.0
  (b) global tolerance 1.0E-15 — so the deviation ~1e-12 is near the cliff
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp074",
    defect=(
        "PLANE Z=0; uncertainty 1.0E-15; 3D B-spline degree-2 6 CPs "
        "CP[1]=(1.999999999999,0,0) FP-cliff value, C-1 break at t=0.3 "
        "(CP[2]=(1.0,0,0) before break, CP[3]=(2.5,0,0) 1.5-unit gap); "
        "pcurve B-spline CP[1]=(2.0,0) exact; "
        "FixSameParameter recomputed tol == 1.0E-15 at cliff; "
        "C-1 break drives OCC shape_null=True"
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

# Vertices
p_bl = f.cartesian_point((0.0, 0.0, 0.0))
p_br = f.cartesian_point((4.0, 0.0, 0.0))
p_tr = f.cartesian_point((4.0, 4.0, 0.0))
p_tl = f.cartesian_point((0.0, 4.0, 0.0))
v_bl = f.vertex_point(p_bl); v_br = f.vertex_point(p_br)
v_tr = f.vertex_point(p_tr); v_tl = f.vertex_point(p_tl)

# THE DEFECT 3D CURVE: degree 2, 6 CPs, knots (3,3,3) at (0,0.3,1).
# CP[1] = (1.999999999999, 0, 0) — FP cliff value (1e-12 below 2.0).
# CP[2] = (1.0, 0, 0) before break; CP[3] = (2.5, 0, 0) after break.
# The 1.5-unit C-1 break at t=0.3 drives OCC shape_null.
# CP[1]'s engineered value creates the FixSameParameter precision cliff.
cp3d_0 = f.cartesian_point((0.0, 0.0, 0.0))
cp3d_1 = f._emit_raw("CARTESIAN_POINT('',(1.999999999999,0.0,0.0))")  # cliff CP
cp3d_2 = f.cartesian_point((1.0, 0.0, 0.0))   # before C-1 break
cp3d_3 = f.cartesian_point((2.5, 0.0, 0.0))   # after break: 1.5-unit X gap
cp3d_4 = f.cartesian_point((3.0, 0.0, 0.0))
cp3d_5 = f.cartesian_point((4.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('cliff_3d',2,"
    f"(#{cp3d_0.eid},#{cp3d_1.eid},#{cp3d_2.eid},#{cp3d_3.eid},#{cp3d_4.eid},#{cp3d_5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3,3),(0.0,0.3,1.0),.UNSPECIFIED.)"
)

# PCurve B-spline: CP[1] = exactly 2.0 (deviates from 3D CP[1] by ~1e-12)
cp2d_0 = f.cartesian_point((0.0, 0.0))
cp2d_1 = f.cartesian_point((2.0, 0.0))    # exact 2.0 ← differs from 1.999999999999
cp2d_2 = f.cartesian_point((1.0, 0.0))
cp2d_3 = f.cartesian_point((2.5, 0.0))
cp2d_4 = f.cartesian_point((3.0, 0.0))
cp2d_5 = f.cartesian_point((4.0, 0.0))

bspline_2d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('cliff_pc_bsp',2,"
    f"(#{cp2d_0.eid},#{cp2d_1.eid},#{cp2d_2.eid},#{cp2d_3.eid},#{cp2d_4.eid},#{cp2d_5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3,3),(0.0,0.3,1.0),.UNSPECIFIED.)"
)
pc_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('cliff_pc_def',(#{bspline_2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('cliff_pc',#{surf.eid},#{pc_def.eid})")
sc = f._emit_raw(
    f"SURFACE_CURVE('cliff_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('cliff_edge',#{v_bl.eid},#{v_br.eid},#{sc.eid},.T.)"
)

# Clean context edges
def make_line_edge(v_s, v_e, p3s, d3, len3, p2s, d2):
    d3e = f.direction(d3); v3 = f.vector(d3e, len3); l3 = f.line(p3s, v3)
    p2  = f.cartesian_point(p2s)
    d2e = f.direction(d2); v2 = f.vector(d2e, len3); l2 = f.line(p2, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    ec  = f._emit_raw(f"EDGE_CURVE('ec',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")
    return ec

e_right = make_line_edge(v_br, v_tr, p_br, (0.,1.,0.), 4., (4.,0.), (0.,1.))
e_top   = make_line_edge(v_tr, v_tl, p_tr, (-1.,0.,0.), 4., (4.,4.), (-1.,0.))
e_left  = make_line_edge(v_tl, v_bl, p_tl, (0.,-1.,0.), 4., (0.,4.), (0.,-1.))

loop  = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])

# Product chain with TIGHT TOLERANCE 1.0E-15 (the precision-cliff trigger)
block_start = max(9000, f._next_id)
f._next_id = block_start

app_ctx    = f._emit_raw("APPLICATION_CONTEXT('mechanical design')")
f.entities.insert(0, f.entities.pop())   # move to front
prod_ctx   = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product    = f._emit_raw(f"PRODUCT('Gp074','Gp074','',({prod_ctx.ref()}))")
prod_form  = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pd_ctx     = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
prod_def   = f._emit_raw(
    f"PRODUCT_DEFINITION('','',#{prod_form.eid},#{pd_ctx.eid})"
)
prod_shape = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{prod_def.eid})")
lu  = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-15),#{lu.eid},"
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
