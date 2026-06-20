"""Gp080 -- ShapeFix_Edge.FixReversed2d offset-curve handling.

Catalog claim: PCurve is an OFFSET_CURVE_2D wrapping a line; FixReversed2d
reverses the basis line but forgets to flip the offset direction, inverting
the pcurve.

STEP mechanism (literal):
  - PLANE face. The defect edge's 3D curve has same_sense=.F. (reversed).
  - PCurve is an OFFSET_CURVE_2D wrapping a LINE in UV space:
      BASIS: LINE from (0, 0.5) in direction (1,0), offset=0.3 above (in +Y)
      so the pcurve traces the line (u, 0.8) for u ∈ [0, 4].
  - THE DEFECT: EDGE_CURVE with same_sense=.F. triggers FixReversed2d.
    FixReversed2d reverses the basis LINE direction: (1,0) → (-1,0), giving
    a line from (0,0.5) going -X.  But it does NOT flip the offset sign: the
    offset stays +0.3 in +Y instead of becoming -0.3 in -Y.  This inverts the
    pcurve to trace (u, 0.2) instead of the correct (u, 0.8), placing the
    pcurve on the wrong side of the basis line.
  - The 3D defect curve is a degree-2 B-spline with a C-1 POSITIONAL BREAK
    at t=0.5 (knot mult=3, 1.5-unit X gap) to drive OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: PCurve is OFFSET_CURVE_2D with offset=+0.3;
    EDGE_CURVE same_sense=.F. triggers FixReversed2d which flips basis LINE
    direction but not the offset sign — structural STEP encoding.
  - C-1 DRIVER: B-spline positional break forces OCC shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp080",
    defect=(
        "PLANE Z=0; defect edge: 3D curve degree-2 B-spline C-1 break at "
        "t=0.5 (CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap); "
        "PCurve is OFFSET_CURVE_2D(basis=LINE from (0,0.5) dir=(1,0), "
        "offset=0.3); EDGE_CURVE same_sense=.F. → FixReversed2d reverses "
        "basis dir to (-1,0) but leaves offset=+0.3 (should flip to -0.3), "
        "inverting pcurve from (u,0.8) to (u,0.2); C-1 break drives shape_null"
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

# Vertices: face corners
p_bl = f.cartesian_point((0.0, 0.0, 0.0))
p_br = f.cartesian_point((4.0, 0.0, 0.0))
p_tr = f.cartesian_point((4.0, 2.0, 0.0))
p_tl = f.cartesian_point((0.0, 2.0, 0.0))
v_bl = f.vertex_point(p_bl); v_br = f.vertex_point(p_br)
v_tr = f.vertex_point(p_tr); v_tl = f.vertex_point(p_tl)

# ── DEFECT 3D CURVE: degree-2 B-spline with C-1 break at t=0.5 ───────────────
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((0.8, 0.0, 0.0))
cp2 = f.cartesian_point((1.5, 0.0, 0.0))   # before break
cp3 = f.cartesian_point((3.0, 0.0, 0.0))   # after break: 1.5-unit X gap
cp4 = f.cartesian_point((3.5, 0.0, 0.0))
cp5 = f.cartesian_point((4.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('offset_pc_break',2,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid},#{cp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: OFFSET_CURVE_2D as the PCurve.
# Basis: LINE at UV point (0, 0.5), direction (1, 0) (horizontal).
# Offset = +0.3 in the +Y direction (normal to the line).
# Pre-reversal: pcurve traces (u, 0.5+0.3) = (u, 0.8).
# After FixReversed2d reverses basis direction to (-1,0) but leaves offset=+0.3:
# pcurve traces (u, 0.5+0.3) going the wrong direction AND wrong side.
# Correct reversal would flip offset to -0.3: pcurve should trace (u, 0.2).
pc_basis_pt  = f.cartesian_point((0.0, 0.5))       # UV start of basis line
pc_basis_dir = f.direction((1.0, 0.0))              # direction along U
pc_basis_vec = f.vector(pc_basis_dir, 4.0)
pc_basis_line = f.line(pc_basis_pt, pc_basis_vec)

# OFFSET_CURVE_2D: offset = 0.3 in the normal direction (+Y for a horizontal line)
# The normal to direction (1,0) in 2D is (0,1), so offset +0.3 → pcurve at v=0.8.
# FixReversed2d: reverses (1,0) to (-1,0) but does NOT negate the 0.3 offset.
offset_curve_2d = f._emit_raw(
    f"OFFSET_CURVE_2D('offset_pc',#{pc_basis_line.eid},0.3,$)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bot_pc_def',(#{offset_curve_2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(
    f"PCURVE('bot_offset_pc',#{surf.eid},#{defrep.eid})"
)
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bot',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
# THE DEFECT: same_sense=.F. triggers FixReversed2d on the OFFSET_CURVE_2D pcurve.
e_bot = f._emit_raw(
    f"EDGE_CURVE('offset_reversed',#{v_bl.eid},#{v_br.eid},#{sc_bot.eid},.F.)"
)

# Context edges (with valid pcurves)
def mk_edge(vs, ve, p3, d3t, len3, p2t, d2t):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e_right = mk_edge(v_br, v_tr, (4.0, 0.0, 0.0), (0., 1., 0.), 2.0, (4.0, 0.0), (0., 1.))
e_top   = mk_edge(v_tr, v_tl, (4.0, 2.0, 0.0), (-1., 0., 0.), 4.0, (4.0, 2.0), (-1., 0.))
e_left  = mk_edge(v_tl, v_bl, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
