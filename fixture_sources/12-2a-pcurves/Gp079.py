"""Gp079 -- ShapeAnalysis_Edge.CheckOverlapping degenerate-pcurve.

Catalog claim: One edge's pcurve is degenerate (collapsed to a point).
CheckOverlapping's 2D intersection logic reports a false overlap with
non-degenerate edges.

STEP mechanism (literal):
  - PLANE face. The defect edge has a PCurve that is degenerate: it is a
    PCURVE built from a DEFINITIONAL_REPRESENTATION containing a LINE whose
    VECTOR has magnitude=0.0 (zero-length direction vector in UV space).
    This collapses the pcurve to a single UV point (0,0).
  - CheckOverlapping computes 2D bounding boxes; the degenerate pcurve's
    "box" degenerates to a point at (0,0), which overlaps every edge that
    passes through (0,0) in UV — causing false overlap reports.
  - The 3D defect curve is a degree-2 B-spline with a C-1 POSITIONAL BREAK
    at t=0.5 (knot mult=3, 1.5-unit X gap) to drive OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: pcurve's UV direction vector has magnitude=0.0,
    collapsing the pcurve to a point — VECTOR entity magnitude field is
    literally 0.0 in the STEP bytes.
  - C-1 DRIVER: B-spline positional break drives OCC shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp079",
    defect=(
        "PLANE Z=0; defect edge: 3D curve degree-2 B-spline C-1 break at "
        "t=0.5 (CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap); PCurve "
        "DEGENERATE: DEFINITIONAL_REPRESENTATION contains LINE with VECTOR "
        "magnitude=0.0 (zero-length), collapsing pcurve to UV point (0,0); "
        "CheckOverlapping 2D box of (0,0) falsely overlaps adjacent edges; "
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
p_tr = f.cartesian_point((4.0, 2.0, 0.0))
p_tl = f.cartesian_point((0.0, 2.0, 0.0))
v_bl = f.vertex_point(p_bl); v_br = f.vertex_point(p_br)
v_tr = f.vertex_point(p_tr); v_tl = f.vertex_point(p_tl)

# ── DEFECT 3D CURVE: degree-2 B-spline with C-1 break at t=0.5 ───────────────
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((0.8, 0.0, 0.0))
cp2 = f.cartesian_point((1.5, 0.0, 0.0))   # before break
cp3 = f.cartesian_point((3.0, 0.0, 0.0))   # after break: 1.5-unit gap
cp4 = f.cartesian_point((3.5, 0.0, 0.0))
cp5 = f.cartesian_point((4.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('degen_3d',2,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid},#{cp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: DEGENERATE pcurve.
# VECTOR magnitude = 0.0 → collapses the pcurve to point (0,0) in UV.
pc_pt  = f.cartesian_point((0.0, 0.0))      # UV anchor point = (0,0)
pc_dir = f.direction((1.0, 0.0))            # direction (doesn't matter; mag=0)
# Emit VECTOR with magnitude=0.0 explicitly via _emit_raw
pc_vec_zero = f._emit_raw(
    f"VECTOR('degen_vec',#{pc_dir.eid},0.0)"
)
pc_line_degen = f._emit_raw(
    f"LINE('degen_line',#{pc_pt.eid},#{pc_vec_zero.eid})"
)
defrep_degen = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bot_pc_def',(#{pc_line_degen.eid}),#{prc.eid})"
)
pcurve_degen = f._emit_raw(
    f"PCURVE('bot_degen_pc',#{surf.eid},#{defrep_degen.eid})"
)
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bot',#{bspline_3d.eid},(#{pcurve_degen.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('degen_pc_edge',#{v_bl.eid},#{v_br.eid},#{sc_bot.eid},.T.)"
)

# Context edges with valid pcurves (these pass through (0,0) in UV, enabling
# the false-overlap intersection that CheckOverlapping would report)
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
# left edge passes through UV (0,0) area — enables the false-overlap trigger
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
