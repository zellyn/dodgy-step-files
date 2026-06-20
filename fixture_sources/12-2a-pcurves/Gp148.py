"""Gp148 — D3 third derivative zero; falls back to line endpoints

Catalog claim: Edge pcurve segment with all derivatives zero up to D3
(low-degree locally flat segment). GetEndTangent2d resorts to linear
interpolation between endpoints without reporting complete degeneracy.
Analyzer fails to detect when all fallback sources exhaust.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge having a PCurve that is locally
    flat at both endpoints so all derivatives D1, D2, D3 vanish.
  - THE CATALOG MECHANISM: Degree-3 B-spline 2D pcurve where the first
    four control points (degree+1) are all coincident at (0.5, 0.5) and
    the last four are all coincident at (1.5, 0.5). This forces
    D1=D2=D3=0 at both t=0 and t=1. GetEndTangent2d exhausts D1, D2, D3
    cascades and falls back to linear interpolation from endpoints
    (0.5,0.5)→(1.5,0.5) without detecting or reporting complete
    degeneracy. OCC heals via endpoint fallback → shape(1)/shape(1).
  - 3D curve: clean LINE from (0,0,0) to (5,0,0). Geometry is valid.
  - NO C-1 break (Archetype B: OCC silently heals).

Mechanism vs driver:
  - CATALOG MECHANISM: PCurve degree-3 B-spline with 4 coincident CPs
    at each end; D1=D2=D3=0 at both endpoints; GetEndTangent2d falls back
    to line endpoints without reporting complete degeneracy;
    derivative_complete_degeneracy; GET_END_TANGENT_2D_B008.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp148",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; "
        "3D LINE from (0,0,0) to (5,0,0) (clean, loadable); "
        "PCurve B_SPLINE_CURVE_WITH_KNOTS degree-3 with 4 coincident CPs "
        "at each end: CP[0..3]=(0.5,0.5) CP[4..7]=(1.5,0.5); "
        "D1=D2=D3=0 at both t=0 and t=1; "
        "GetEndTangent2d exhausts all derivative fallbacks and resorts to "
        "linear interpolation between endpoints (0.5,0.5) and (1.5,0.5) "
        "without reporting complete degeneracy; "
        "derivative_complete_degeneracy GET_END_TANGENT_2D_B008; "
        "OCC heals via endpoint fallback → shape(1)/shape(1)"
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
# NO C-1 DRIVER: Archetype B — OCC heals, expected shape(1)/shape(1).
# 3D curve: clean LINE from (0,0,0) to (5,0,0).
line_3d_orig = f.cartesian_point((0.0, 0.0, 0.0))
line_3d_dir  = f.direction((1.0, 0.0, 0.0))
line_3d_vec  = f.vector(line_3d_dir, 5.0)
line_3d      = f.line(line_3d_orig, line_3d_vec)

# THE CATALOG MECHANISM: Degree-3 B-spline PCurve, 4 coincident CPs at each end.
# CP[0..3] all at (0.5, 0.5): entire initial Bezier segment is a degenerate point.
# CP[4..7] all at (1.5, 0.5): entire final Bezier segment is also a degenerate point.
# For a degree-3 curve with k+1 = 8 control points:
#   D1(0) = 3*(CP[1]-CP[0]) / (t[4]-t[1]) = 3*(0,0)/span = (0,0).
#   D2(0) = 0, D3(0) = 0 (all CPs in first span coincident).
#   Similarly D1(1)=D2(1)=D3(1)=0 (last span fully coincident).
# GetEndTangent2d cascade: D1=0 → D2=0 → D3=0 → endpoint line (0.5,0.5)→(1.5,0.5).
# Tangent derived silently as (1,0) from endpoint geometry. Degeneracy unreported.
qp0 = f.cartesian_point((0.5, 0.5))   # coincident block at start
qp1 = f.cartesian_point((0.5, 0.5))
qp2 = f.cartesian_point((0.5, 0.5))
qp3 = f.cartesian_point((0.5, 0.5))
qp4 = f.cartesian_point((1.5, 0.5))   # coincident block at end
qp5 = f.cartesian_point((1.5, 0.5))
qp6 = f.cartesian_point((1.5, 0.5))
qp7 = f.cartesian_point((1.5, 0.5))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('d3_zero_endpoint_fallback_pc',3,"
    f"(#{qp0.eid},#{qp1.eid},#{qp2.eid},#{qp3.eid},"
    f"#{qp4.eid},#{qp5.eid},#{qp6.eid},#{qp7.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,4),(0.0,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('d3_zero_endpoint_fallback_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('d3_zero_endpoint_fallback_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('d3_zero_endpoint_fallback_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('d3_zero_endpoint_fallback_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
