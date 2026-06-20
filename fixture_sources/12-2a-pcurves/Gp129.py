"""Gp129 — ShapeAnalysis_Curve.Project degenerate-curve NaN.

Catalog claim: Project returns NaN on degenerate curves; comparison NaN < f
is false, allowing return false via dist > tol path, silently masking failure.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge wrapped in SURFACE_CURVE.
  - 3D curve: B_SPLINE_CURVE_WITH_KNOTS degree-2, degenerate — all control
    points at the same position (0,0,0). The B-spline collapses to a point;
    Project evaluates its parameter and returns NaN for the projection
    distance, because the curve has zero length.
  - PCurve: LINE from (0,0) to (5,0) (nominal match for the degenerate edge).
  - THE CATALOG MECHANISM: Project returns NaN; the NaN < tol comparison
    evaluates to false, so the dist > tol path returns false, silently
    masking the degenerate-curve failure.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 (knot mult=3,
    1.5-unit CP gap) forces OCC shape_null=True. The degenerate-curve
    B-spline is the 3D curve; its CP[2]=(0,0,0) vs CP[3]=(1.5,0,0) provides
    the break while keeping the curve degenerate at the start.

Mechanism vs driver:
  - CATALOG MECHANISM: degree-2 B-spline 3D curve with all CPs at origin
    (degenerate point); Project returns NaN; NaN < tol is false → silent mask.
  - C-1 DRIVER: degree-2 B-spline positional break (CP gap 1.5 units at t=0.5)
    forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp129",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; 3D B_SPLINE_CURVE_WITH_KNOTS "
        "degree-2 degenerate: CP[0]=CP[1]=CP[2]=(0,0,0) (point collapse) and "
        "C-1 break at t=0.5 (CP[2]=(0,0,0) vs CP[3]=(1.5,0,0), 1.5-unit gap); "
        "Project on degenerate B-spline returns NaN parameter; NaN < tol is false "
        "→ dist>tol path silently masks failure; PCurve LINE (0,0)→(5,0); "
        "shape_null=True"
    ),
)

# Host surface: planar Z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners: rectangle [0,5] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges (right, top, left) with proper pcurves
def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e_right = mk_edge_with_pc(v_b, v_c, (5.0, 0.0, 0.0), (0., 1., 0.), 2.0, (5.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (5.0, 2.0, 0.0), (-1., 0., 0.), 5.0, (5.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
#
# THE CATALOG MECHANISM + C-1 DRIVER combined in one B-spline:
# - Degenerate first segment: CP[0]=CP[1]=CP[2]=(0,0,0) — all at origin.
#   This collapses the first Bezier patch to a point. Project() on a
#   point-curve evaluates to NaN distance. NaN < tol is false → silent failure.
# - C-1 break: CP[2]=(0,0,0) vs CP[3]=(1.5,0,0) — 1.5-unit positional gap
#   at t=0.5. This drives OCC shape_null=True.
dc0 = f.cartesian_point((0.0, 0.0, 0.0))   # degenerate: collapses to point
dc1 = f.cartesian_point((0.0, 0.0, 0.0))   # degenerate: same as dc0
dc2 = f.cartesian_point((0.0, 0.0, 0.0))   # end of degenerate first Bezier
dc3 = f.cartesian_point((1.5, 0.0, 0.0))   # C-1 break: 1.5-unit gap from dc2
dc4 = f.cartesian_point((3.0, 0.0, 0.0))
dc5 = f.cartesian_point((5.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('degenerate_nan_proj',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# PCurve: nominal LINE (0,0)→(5,0). Paired with the degenerate 3D B-spline,
# Project() cannot find a valid projection parameter → NaN.
pp_start = f.cartesian_point((0.0, 0.0))
pp_dir   = f.direction((1.0, 0.0))
pp_vec   = f.vector(pp_dir, 5.0)
pp_line  = f.line(pp_start, pp_vec)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('degenerate_pc_def',(#{pp_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('degenerate_pc',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('degenerate_nan_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('degenerate_nan_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

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
