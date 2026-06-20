"""Gp169 — ProjectDegenerated.dual-distance-logic

Catalog claim: B-spline surface with 3D curve initial gap. Pcurve distance metrics
inconsistently recompute; direct vs. recomputed gap comparison diverges.
OCC silently heals; produces shape(1)/shape(1).

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS face with a defect edge whose 3D curve has a
    small initial positional gap (not a C-1 break — a legitimate surface-fitting
    gap). The pcurve distance metrics are computed twice: once directly from the
    STEP geometry and once via recomputed projection. These two gap values diverge,
    causing dual-distance-logic to produce an inconsistent result. OCC heals the
    divergence silently.
  - THE CATALOG MECHANISM (dual-distance-logic): ProjectDegenerated uses two
    distance comparisons for the pcurve. The first measures the gap between the
    initial 3D point on the curve and the projected point on the surface. The
    second recomputes the gap from the current parametric position. For a B-spline
    surface with a small initial fitting gap (not a C-1 break), these two measures
    diverge because the surface parametrization is non-uniform; the dual comparison
    logic cannot resolve which measure to trust; OCC's healing accepts the closer
    projection and produces shape(1)/shape(1).
  - NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree 2x2; defect edge has a
    small 3D initial gap (0.08 units, within heal threshold) not a C-1 break;
    pcurve distance: direct measurement vs. recomputed projection diverge due to
    non-uniform surface parametrization; dual-distance-logic inconsistency; OCC
    heals silently; load == "ok".
  - NO C-1 DRIVER: Archetype B — geometry is loadable.

Distinction from Gp160 (singularity-tolerance-threshold, shape(1)): Gp160 uses
a cone with singularity tolerance mismatch; Gp169 uses a B-spline surface where
the two distance metrics in ProjectDegenerated diverge due to non-uniform
parametrization and a small initial fitting gap.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp169",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree 2x2; defect edge: SURFACE_CURVE; "
        "3D LINE with small initial positional gap (0.08 units, sub-heal-threshold, "
        "not a C-1 break); "
        "pcurve LINE in UV from (0,0) to (0,1) on non-uniform B-spline surface; "
        "ProjectDegenerated dual-distance: direct gap vs. recomputed projection "
        "diverge due to non-uniform parametrization; inconsistent distance logic; "
        "dual-distance-logic axis; OCC heals silently; load == ok"
    ),
)

# B_SPLINE_SURFACE_WITH_KNOTS: degree 2 in both u and v.
# A simple 3x3 control-point grid defining a slightly curved surface over [0,1]x[0,1].
# The slight curvature makes the parametrization non-uniform so the dual-distance
# measures diverge for an edge with an initial gap.
#
# Control points: 3x3 grid, surface bows slightly upward in the middle.
# Row 0 (v=0): (0,0,0), (0.5,0,0), (1,0,0)
# Row 1 (v=0.5): (0,0.5,0.1), (0.5,0.5,0.15), (1,0.5,0.1) — slight bow
# Row 2 (v=1): (0,1,0), (0.5,1,0), (1,1,0)
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p01 = f.cartesian_point((0.5, 0.0, 0.0))
p02 = f.cartesian_point((1.0, 0.0, 0.0))
p10 = f.cartesian_point((0.0, 0.5, 0.1))
p11 = f.cartesian_point((0.5, 0.5, 0.15))
p12 = f.cartesian_point((1.0, 0.5, 0.1))
p20 = f.cartesian_point((0.0, 1.0, 0.0))
p21 = f.cartesian_point((0.5, 1.0, 0.0))
p22 = f.cartesian_point((1.0, 1.0, 0.0))

# B_SPLINE_SURFACE_WITH_KNOTS: degree 2x2, 3x3 control points, open (clamped) knots.
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('bspline_dual_distance',2,2,"
    f"((#{p00.eid},#{p01.eid},#{p02.eid}),"
    f"(#{p10.eid},#{p11.eid},#{p12.eid}),"
    f"(#{p20.eid},#{p21.eid},#{p22.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3),(3,3),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners on the surface boundary (u,v) in [0,1]x[0,1].
# 3D corners from the clamped B-spline boundary (coincide with corner CPs).
A3 = (0.0, 0.0, 0.0)   # (u=0, v=0)
B3 = (1.0, 0.0, 0.0)   # (u=1, v=0)
C3 = (1.0, 1.0, 0.0)   # (u=1, v=1)
D3 = (0.0, 1.0, 0.0)   # (u=0, v=1)

p_A = f.cartesian_point(A3); v_A = f.vertex_point(p_A)
p_B = f.cartesian_point(B3); v_B = f.vertex_point(p_B)
p_C = f.cartesian_point(C3); v_C = f.vertex_point(p_C)
p_D = f.cartesian_point(D3); v_D = f.vertex_point(p_D)

def mk_line_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t, len2):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve on B-spline surface."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2e = f.vector(d2e, len2); l2 = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Edge B→C: right side (u=1, v from 0 to 1).
e_BC = mk_line_edge_with_pc(
    v_B, v_C, B3, (0., 1., 0.), 1.0, (1.0, 0.0), (0.0, 1.0), 1.0
)

# Edge C→D: top (v=1, u from 1 to 0).
e_CD = mk_line_edge_with_pc(
    v_C, v_D, C3, (-1., 0., 0.), 1.0, (1.0, 1.0), (-1.0, 0.0), 1.0
)

# Edge D→A: left side (u=0, v from 1 to 0).
e_DA = mk_line_edge_with_pc(
    v_D, v_A, D3, (0., -1., 0.), 1.0, (0.0, 1.0), (0.0, -1.0), 1.0
)

# ── DEFECT EDGE A→B — bottom (v=0, u from 0 to 1) ────────────────────────────
#
# THE CATALOG MECHANISM: The 3D LINE starts at A3=(0,0,0) but has a small initial
# offset: the 3D curve starts at (0.08, 0, 0) instead of (0,0,0). This 0.08-unit
# initial positional gap (well below OCC's healing threshold of ~0.1) simulates a
# surface-fitting gap, not a C-1 break. ProjectDegenerated's dual-distance logic
# measures this gap directly (large: 0.08) vs. recomputed from projection
# (small: < tolerance). The divergence between direct and recomputed measures
# causes inconsistent behavior in the dual-distance comparison; OCC heals the
# closer projection and produces shape(1)/shape(1).
# NO C-1 break: Archetype B — the 3D curve is continuous and loadable.
line_3d_orig = f.cartesian_point((0.08, 0.0, 0.0))   # small initial gap from A3
line_3d_dir  = f.direction((1.0, 0.0, 0.0))
line_3d_len  = 1.0 - 0.08   # reach B3=(1,0,0)
line_3d_vec  = f.vector(line_3d_dir, line_3d_len)
line_3d      = f.line(line_3d_orig, line_3d_vec)

# PCurve: straight along v=0, u from 0 to 1.
pc_start = f.cartesian_point((0.0, 0.0))
pc_dir   = f.direction((1.0, 0.0))
pc_vec   = f.vector(pc_dir, 1.0)
pc_line  = f.line(pc_start, pc_vec)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('dual_dist_pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('dual_dist_pc',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('dual_dist_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('dual_dist_edge',#{v_A.eid},#{v_B.eid},#{sc_bot.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_BC,  True),
    f.oriented_edge(e_CD,  True),
    f.oriented_edge(e_DA,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
