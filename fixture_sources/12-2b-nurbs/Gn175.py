"""Gn175 — Gordon surface ill-conditioned guide-curve network.

Catalog claim: Lofted/skinned face whose boundary curves form an ill-conditioned
guide-curve network (nearly parallel rail curves with inconsistent
parameterization). Pre-OCCT-V8, GeomFill_Gordon silently produced degenerate
geometry; OCCT V8+ explicitly reports the ill-conditioning and applies a fallback.
Source: OCCT V8_0_0_p1 release note (GitHub Open-Cascade-SAS/OCCT releases).

OCC behavior: On OCCT V8+, GeomFill_Gordon detects the near-parallel rail
configuration and either falls back to ruled/loft or returns a degenerate
surface; the B-spline surface IS the face geometry (mechanism on the defect
entity, not an orphan).

STEP mechanism (literal):
  - Two B_SPLINE_CURVE_WITH_KNOTS guide curves (rail curves) that are nearly
    parallel: both run approximately in the X direction at Z=0 and Z=0.01
    (separation 0.01 mm, far below any typical tolerance). They share the
    same start/end X range [0, 10] but have slightly different Y offsets.
  - A B_SPLINE_SURFACE_WITH_KNOTS loft surface interpolating between these
    nearly-coincident rails; the guide-curve network is ill-conditioned because
    the two rails are nearly parallel and nearly coincident.
  - The surface has a V extent of 0.01 (near-zero), while U spans 10 units,
    producing an extreme aspect ratio in parametric space AND a near-degenerate
    physical extent in V — the exact condition that triggers GeomFill_Gordon
    ill-conditioning.

Historical-fix note: Pre-OCCT-V8, this fixture silently produced incorrect
loft geometry. On OCCT V8+, the fix is present; current behavior may produce
a valid (though degenerate) shape or report a warning. The fixture documents
the defect class regardless of current OCCT behavior.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn175",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS loft over two nearly-parallel "
        "B_SPLINE_CURVE_WITH_KNOTS rail curves (separation 0.01 mm, ratio 1000:1 "
        "to U extent); GeomFill_Gordon ill-conditioned guide-curve network; "
        "pre-OCCT-V8 silently degenerate; OCCT V8_0_0_p1 release note"
    ),
)

# ── DEFECT SURFACE: degree (2,1), 3×2 net, nearly degenerate V extent ─────────
# Rail 1 (v=0): Z=0.00, rail 2 (v=0.01): Z=0.01.
# U spans [0, 10]; V spans [0, 0.01] → aspect ratio 1000:1.
# This recreates the ill-conditioned Gordon network: two nearly-parallel rails
# separated by only 0.01 mm over a U span of 10 mm.
#
# Control point grid (3 U rows × 2 V cols):
#   Row 0 (u=0):   (0,  0, 0.00), (0,  0, 0.01)
#   Row 1 (u=5):   (5,  0, 0.00), (5,  0, 0.01)
#   Row 2 (u=10):  (10, 0, 0.00), (10, 0, 0.01)
#
# U knots: clamped degree-2, 3 poles → mults (3,3) at (0,10); sum=6=3+2+1 ✓
# V knots: clamped degree-1, 2 poles → mults (2,2) at (0,0.01); sum=4=2+1+1 ✓

grid = [
    [f.cartesian_point((0.0,  0.0, 0.0)),  f.cartesian_point((0.0,  0.0, 0.01))],
    [f.cartesian_point((5.0,  0.0, 0.0)),  f.cartesian_point((5.0,  0.0, 0.01))],
    [f.cartesian_point((10.0, 0.0, 0.0)),  f.cartesian_point((10.0, 0.0, 0.01))],
]

surf = f.b_spline_surface_with_knots(
    u_degree=2, v_degree=1,
    control_points_grid=grid,
    u_multiplicities=[3, 3],
    v_multiplicities=[2, 2],
    u_knots=[0.0, 10.0],
    v_knots=[0.0, 0.01],
    surface_form="UNSPECIFIED",
    u_closed=False,
    v_closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
)

# ── Parametric context for pcurves ──
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Corner 3D points matching the surface domain [0,10]×[0,0.01]:
#   (u=0,  v=0)    → (0,  0, 0)
#   (u=10, v=0)    → (10, 0, 0)
#   (u=10, v=0.01) → (10, 0, 0.01)
#   (u=0,  v=0.01) → (0,  0, 0.01)
p_a = f.cartesian_point((0.0,  0.0, 0.0))
p_b = f.cartesian_point((10.0, 0.0, 0.0))
p_c = f.cartesian_point((10.0, 0.0, 0.01))
p_d = f.cartesian_point((0.0,  0.0, 0.01))

v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)


def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t, p2_len):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, len3)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, p2_len)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


# Bottom rail (v=0): p_a → p_b in X, z=0; pcurve u: 0→10, v=0
e_bot   = mk_edge_with_pc(
    v_a, v_b,
    (0.0, 0.0, 0.0),  (1., 0., 0.),  10.0,
    (0.0, 0.0),       (1., 0.),       10.0)

# Right side: p_b → p_c in Z, u=10; pcurve v: 0→0.01, u=10
e_right = mk_edge_with_pc(
    v_b, v_c,
    (10.0, 0.0, 0.0),  (0., 0., 1.),  0.01,
    (10.0, 0.0),       (0., 1.),       0.01)

# Top rail (v=0.01): p_c → p_d, reversed in X; pcurve u: 10→0, v=0.01
e_top   = mk_edge_with_pc(
    v_c, v_d,
    (10.0, 0.0, 0.01), (-1., 0., 0.), 10.0,
    (10.0, 0.01),      (-1., 0.),      10.0)

# Left side: p_d → p_a in Z reversed, u=0; pcurve v: 0.01→0, u=0
e_left  = mk_edge_with_pc(
    v_d, v_a,
    (0.0, 0.0, 0.01),  (0., 0., -1.), 0.01,
    (0.0, 0.01),       (0., -1.),      0.01)

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
