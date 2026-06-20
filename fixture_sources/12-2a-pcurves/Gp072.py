"""Gp072 -- ShapeFix_Edge.FixAddPCurve B-spline projection failure.

Catalog claim: Edge with B-spline 3D curve that deviates from host plane
(~0.001 at midpoint).  FixAddPCurve projection attempts produce geometrically
incorrect pcurve that's "good enough" by tolerance but wrong in geometry.

STEP-level trigger: EDGE_CURVE whose geometry is a bare B_SPLINE_CURVE_WITH_KNOTS
(no SURFACE_CURVE wrapper, no pcurve).  The edge belongs to an ADVANCED_FACE on
a PLANE.  Since there is no pcurve, FixAddPCurve must project the B-spline onto
the plane to build one.  The projection of the off-plane control point (~0.001
in Z) produces an approximated pcurve that accumulates geometric error.

The B-spline also has a C-1 positional break (knot mult=3=degree+1, 1.5-unit
gap in X at t=0.3).  This break causes OCC shape_null=True (the expected
outcome) while also making the FixAddPCurve projection path produce a
geometrically distorted result — the break after projection creates an
incorrect piecewise pcurve with a discontinuous jump.

The 0.001 Z-deviation in the interior control point is the primary FixAddPCurve
trigger; the C-1 X-break drives OCC's transfer to produce shape_null.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp072",
    defect=(
        "PLANE Z=0 face; defect edge geometry is bare B_SPLINE_CURVE_WITH_KNOTS "
        "(degree 2, 6 CPs, knot-mult (3,3,3) at t=(0,0.3,1)); "
        "CP[2]=(1.0,0.0,0.001) deviates 0.001 from plane; "
        "CP[3]=(2.5,0.0,0.0) creates 1.5-unit C-1 break at t=0.3; "
        "no SURFACE_CURVE / no pcurve; FixAddPCurve projects off-plane bspline; "
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

# THE DEFECT: bare B-spline 3D curve (no SURFACE_CURVE wrapper).
# Degree 2, 6 CPs. Knots (3,3,3) at (0.0, 0.3, 1.0):
#   sum(mults) = 3+3+3 = 9 = n_poles(6) + degree(2) + 1 = 9 ✓
# CP[2]=(1.0,0.0,0.001): 0.001 ABOVE Z=0 plane — FixAddPCurve projection trigger.
# CP[3]=(2.5,0.0,0.0): 1.5-unit X gap at t=0.3 — C-1 break driving shape_null.
bc0 = f.cartesian_point((0.0, 0.0, 0.0))
bc1 = f.cartesian_point((0.5, 0.0, 0.0))
bc2 = f.cartesian_point((1.0, 0.0, 0.001))  # off-plane: FixAddPCurve trigger
bc3 = f.cartesian_point((2.5, 0.0, 0.0))    # 1.5-unit C-1 break at t=0.3
bc4 = f.cartesian_point((3.0, 0.0, 0.0))
bc5 = f.cartesian_point((4.0, 0.0, 0.0))

# BARE B-SPLINE — no SURFACE_CURVE, no pcurve.  This is the FixAddPCurve trigger.
bare_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('defect_bspline',2,"
    f"(#{bc0.eid},#{bc1.eid},#{bc2.eid},#{bc3.eid},#{bc4.eid},#{bc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3,3),(0.0,0.3,1.0),.UNSPECIFIED.)"
)

# Defect EDGE_CURVE: geometry is the bare B-spline (no SURFACE_CURVE wrapper)
e_bot = f._emit_raw(
    f"EDGE_CURVE('defect_edge',#{v_bl.eid},#{v_br.eid},#{bare_bspline.eid},.T.)"
)

# Clean context edges with SURFACE_CURVE + PCURVE
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
f.add_product_chain(sbsm)
