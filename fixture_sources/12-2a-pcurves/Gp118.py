"""Gp118 — Very-many-samples high-curvature edge.

Catalog claim: ShapeAnalysis_Edge.CheckCurve3dWithPCurve under-samples long
B-spline with sharp oscillations; log-scaling still misses fine features.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE face with a defect edge wrapped in SURFACE_CURVE.
  - 3D curve: B_SPLINE_CURVE_WITH_KNOTS degree-2 with many oscillating CPs
    that form sharp curvature spikes. The sampling budget (proportional to
    edge length) is insufficient to catch the fine oscillation: even with
    log-scaled sampling the spike regions are skipped.
  - PCurve: matching B-spline in UV whose oscillation is similarly fine.
  - THE CATALOG MECHANISM: CheckCurve3dWithPCurve's adaptive sampling uses
    n_samples proportional to the B-spline degree and segment count. On a
    long, high-curvature B-spline the sample density is too low; the algorithm
    log-scales but still misses the curvature spike at t≈0.35. The pcurve
    consistency check passes despite the real 3D/2D mismatch in the spike.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 (knot mult=3,
    1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: many-segment B-spline with sharp oscillation; sampling
    budget misses spike at t≈0.35 (log-scaling still insufficient).
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 forces shape_null.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp118",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; 3D B_SPLINE_CURVE_WITH_KNOTS "
        "degree-2 8 CPs 4 spans (3,1,1,1,3) at (0.0,0.25,0.5,0.75,1.0); "
        "CP[2]=(1.5,0.6,0) spike (curvature ~3.5/unit); CP[3]=(1.5,0,0) vs "
        "CP[4]=(3.0,0,0) 1.5-unit C-1 gap at t=0.5 drives shape_null; "
        "PCurve B-spline degree-2 matching span structure with oscillation at "
        "t=0.25 span; CheckCurve3dWithPCurve log-scaled sampling misses spike "
        "at t≈0.35; shape_null=True"
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
# THE CATALOG MECHANISM: degree-2 B-spline with 4 spans and a sharp curvature
# spike at t≈0.35. The sampling budget for CheckCurve3dWithPCurve is proportional
# to the number of Bezier segments. With 4 segments and degree 2 the adaptive
# log-scaled sampling uses n≈8–12 points — insufficient to resolve the spike
# at t≈0.35 where curvature ≈ 3.5/unit (radius ~ 0.29). The spike is between
# adjacent sample points and is silently skipped.
#
# C-1 DRIVER: knot mult=3 at t=0.5 with CP[3]=(1.5,0,0) vs CP[4]=(3.0,0,0)
# (1.5-unit gap) forces OCC shape_null=True.
#
# Knot vector: (3,1,1,1,3) at (0.0, 0.25, 0.5, 0.75, 1.0) → 4 spans, 8 CPs.
dc0 = f.cartesian_point((0.0,  0.0,  0.0))   # start
dc1 = f.cartesian_point((0.4,  0.0,  0.0))   # smooth
dc2 = f.cartesian_point((0.9,  0.65, 0.0))   # spike peak: curvature ~3.5/unit
dc3 = f.cartesian_point((1.5,  0.0,  0.0))   # end of spike / first half
dc4 = f.cartesian_point((3.0,  0.0,  0.0))   # C-1 break: 1.5-unit gap
dc5 = f.cartesian_point((3.7,  0.0,  0.0))
dc6 = f.cartesian_point((4.3,  0.0,  0.0))
dc7 = f.cartesian_point((5.0,  0.0,  0.0))   # end

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('highcurv_spike',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},"
    f"#{dc4.eid},#{dc5.eid},#{dc6.eid},#{dc7.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,1,1,1,3),(0.0,0.25,0.5,0.75,1.0),.UNSPECIFIED.)"
)

# PCurve: degree-2 B-spline in UV with matching span structure and spike at t≈0.25.
# The UV spike is deliberately offset from the 3D spike (at t≈0.35 in 3D) so that
# CheckCurve3dWithPCurve's uniform sampling between sample points misses the mismatch.
pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.5,  0.0))
pp2 = f.cartesian_point((1.0,  0.45))   # UV spike: disagreement with 3D spike position
pp3 = f.cartesian_point((1.5,  0.0))
pp4 = f.cartesian_point((3.0,  0.0))
pp5 = f.cartesian_point((3.8,  0.0))
pp6 = f.cartesian_point((4.4,  0.0))
pp7 = f.cartesian_point((5.0,  0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('highcurv_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},"
    f"#{pp4.eid},#{pp5.eid},#{pp6.eid},#{pp7.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,1,1,1,3),(0.0,0.25,0.5,0.75,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('highcurv_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('highcurv_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('highcurv_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('highcurv_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
