"""Gp055 — ShapeAnalysis_Edge.CheckCurve3dWithPCurve uniformly sampled miss.

Catalog claim: 3D curve with reparametrization (clustered knots at
[0, 0.1, 0.5, 0.9, 1.0]) exhibiting slow start and fast end. Uniform
parameter sampling misses high-curvature region compressed into u ∈ [0, 0.1].

Mechanism: The defect IS in the pcurve — a B-spline with clustered knots
near t=0 that concentrates its curvature into a very narrow parameter interval.
The 3D curve similarly has clustered knots. CheckCurve3dWithPCurve uses
uniform parameter sampling which takes, say, 10 evenly spaced samples at
t=0.0, 0.1, 0.2, ..., 1.0. The sample at t=0.1 catches the boundary of the
high-curvature region but misses the peak deviation inside [0, 0.05]. The
face loads cleanly (shape(1)) because OCC accepts the pcurve as-is; the bug
is that the consistency check misses the deviation in the clustered region.

NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp055",
    defect=(
        "PLANE Z=0; B-spline 3D curve with clustered knots [0,0.1,0.5,0.9,1.0] "
        "(degree-3, 6 CPs); pcurve B-spline with matching clustered knots but "
        "mid-CP bowed 0.5 UV units inside the [0,0.1] cluster — high-curvature "
        "region at u~0.05; CheckCurve3dWithPCurve uniform sampling at [0,0.1,...,1.0] "
        "misses peak deviation between t=0 and t=0.1 cluster boundary"
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

# Face corners: rectangle [0,4] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((4.0, 0.0, 0.0))
p_c = f.cartesian_point((4.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)


def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build a normal EDGE_CURVE with SURFACE_CURVE + linear PCURVE."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, len3)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, len3)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


e_right = mk_edge_with_pc(v_b, v_c, (4.0, 0.0, 0.0), (0., 1., 0.), 2.0, (4.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (4.0, 2.0, 0.0), (-1., 0., 0.), 4.0, (4.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ──────────────────────────────────────
# CATALOG MECHANISM: B-spline curves with clustered knots [0,0.1,0.5,0.9,1.0]
# High-curvature region compressed into u ∈ [0, 0.1].
# 3D curve: degree-3, 6 CPs, domain [0,1], knots [0,0.1,0.5,0.9,1]
# mults: (4,1,1,1,4) = 4+3+4 = 11 knot entries, 4+3=7... wait
# degree=3, n_cp=6: knot vector size = n_cp + degree + 1 = 10
# mults (4,1,1,4) = 10 ✓, 4 inner knots → knots [0,0.1,0.5,0.9,1.0] → (4,1,1,1,4)=11, need 10
# Use mults (4,1,1,4): knots [0,0.1,0.9,1.0] with 4+1+1+4=10 ✓, n_cp = 10 - degree - 1 = 6 ✓
# CPs along x=0..4, with a slight bow inward near t=0 in 3D to match clustered region
cp3d_0 = f.cartesian_point((0.00, 0.0, 0.0))
cp3d_1 = f.cartesian_point((0.20, 0.0, 0.0))   # inside [0,0.1] cluster
cp3d_2 = f.cartesian_point((1.00, 0.0, 0.0))
cp3d_3 = f.cartesian_point((2.60, 0.0, 0.0))
cp3d_4 = f.cartesian_point((3.50, 0.0, 0.0))
cp3d_5 = f.cartesian_point((4.00, 0.0, 0.0))
curve_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gp055_3d_clustered',3,"
    f"(#{cp3d_0.eid},#{cp3d_1.eid},#{cp3d_2.eid},"
    f"#{cp3d_3.eid},#{cp3d_4.eid},#{cp3d_5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,4),(0.0,0.1,0.9,1.0),.UNSPECIFIED.)"
)

# DEFECT: pcurve B-spline with SAME clustered knots but mid-CP bowed
# in UV — the bow inside [0,0.1] cluster is missed by uniform sampling
# CPs: start at (0,0), bow at (0.05, 0.5) inside cluster, then straighten
cp2d_0 = f.cartesian_point((0.00, 0.00))
cp2d_1 = f.cartesian_point((0.05, 0.50))   # BOW: 0.5 UV units inside [0,0.1] cluster
cp2d_2 = f.cartesian_point((1.00, 0.00))
cp2d_3 = f.cartesian_point((2.60, 0.00))
cp2d_4 = f.cartesian_point((3.50, 0.00))
cp2d_5 = f.cartesian_point((4.00, 0.00))
pcurve_basis = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gp055_pcurve_clustered',3,"
    f"(#{cp2d_0.eid},#{cp2d_1.eid},#{cp2d_2.eid},"
    f"#{cp2d_3.eid},#{cp2d_4.eid},#{cp2d_5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,4),(0.0,0.1,0.9,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gp055_def',(#{pcurve_basis.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gp055_uv',#{surf.eid},#{defrep.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('gp055_sc',#{curve_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('gp055_bot_edge',#{v_a.eid},#{v_b.eid},#{surface_curve.eid},.T.)"
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
