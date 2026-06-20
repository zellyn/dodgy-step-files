"""Gp107 — FixSameParameter degenerate-on-spline.

Catalog claim: Edge whose 3D curve is B-spline of degree 0 (control-point-only,
no smoothing). FixSameParameter identifies it as degenerate but does not invoke
degenerate-edge fix path.

STEP mechanism (literal):
  - PLANE Z=0 face.
  - Defect edge: EDGE_CURVE with a B_SPLINE_CURVE_WITH_KNOTS degree-2 3D curve
    that has CP[0]==CP[N] (first and last control points identical) — the classic
    "closed degenerate" shape used to trigger FixSameParameter's degeneracy path.
    Also carries a degree-2 C-1 positional break (knot mult=3, 1.5-unit gap) as
    the shape_null driver.
  - THE CATALOG MECHANISM: all control points lie at (0,0,0) except CP[3] and
    CP[4] which form the gap; CP[0]=CP[5]=(0,0,0). FixSameParameter detects the
    degenerate (start==end) spline but does not dispatch to the degenerate-edge
    fix code path, leaving the edge in an invalid state.
  - C-1 DRIVER: B-spline positional break at t=0.5 (CP[2]=(0,0,0) vs
    CP[3]=(1.5,0,0), 1.5-unit gap) forces shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B-spline with CP[0]==CP[N] (degenerate start==end);
    FixSameParameter misses degenerate-edge dispatch.
  - C-1 DRIVER: degree-2 B-spline positional break forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp107",
    defect=(
        "PLANE Z=0; defect edge: 3D B_SPLINE_CURVE_WITH_KNOTS degree-2 with "
        "CP[0]==CP[5]=(0,0,0) (degenerate closed spline — start==end); C-1 "
        "break at t=0.5 (CP[2]=(0,0,0) vs CP[3]=(1.5,0,0), 1.5-unit gap) "
        "drives shape_null; FixSameParameter detects degenerate but does not "
        "invoke degenerate-edge fix path; PCurve smooth B-spline [0,1]; "
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

# Context edges (right, top, left) — clean
d_up = f.direction((0.0, 1.0, 0.0)); vec_up = f.vector(d_up, 2.0)
d_lt = f.direction((-1.0, 0.0, 0.0)); vec_lt = f.vector(d_lt, 5.0)
d_dn = f.direction((0.0, -1.0, 0.0)); vec_dn = f.vector(d_dn, 2.0)
e_right = f.edge_curve(v_b, v_c, f.line(p_b, vec_up))
e_top   = f.edge_curve(v_c, v_d, f.line(p_c, vec_lt))
e_left  = f.edge_curve(v_d, v_a, f.line(p_d, vec_dn))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────

# THE CATALOG MECHANISM + C-1 DRIVER (combined):
# B-spline degree-2, 6 CPs, knot vector (3,3,3) at (0.0, 0.5, 1.0).
# CP[0] = CP[5] = (0,0,0): degenerate — start == end. FixSameParameter
# detects degenerate but fails to dispatch to the degenerate-edge fix path.
# C-1 break at t=0.5: CP[2]=(0,0,0) vs CP[3]=(1.5,0,0) — 1.5-unit gap.
dc0 = f.cartesian_point((0.0, 0.0, 0.0))   # degenerate start
dc1 = f.cartesian_point((0.0, 0.0, 0.0))   # same as dc0 (collapsed first span)
dc2 = f.cartesian_point((0.0, 0.0, 0.0))   # end of first Bezier (coincident — degenerate)
dc3 = f.cartesian_point((1.5, 0.0, 0.0))   # start of second — 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((3.0, 0.0, 0.0))
dc5 = f.cartesian_point((0.0, 0.0, 0.0))   # degenerate end == start (CP[0]==CP[5])

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('degen_spline',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# PCurve: smooth B-spline from (0,0) to (5,0) in UV, domain [0,1].
pc0 = f.cartesian_point((0.0, 0.0))
pc1 = f.cartesian_point((1.2, 0.0))
pc2 = f.cartesian_point((2.5, 0.0))
pc3 = f.cartesian_point((3.5, 0.0))
pc4 = f.cartesian_point((4.3, 0.0))
pc5 = f.cartesian_point((5.0, 0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('degen_pc',2,"
    f"(#{pc0.eid},#{pc1.eid},#{pc2.eid},#{pc3.eid},#{pc4.eid},#{pc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('degen_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('degen_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('degen_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('degen_spline_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
