"""Gn001 — B_SPLINE_SURFACE_WITH_KNOTS U knots duplicated without justifying multiplicity.

Catalog claim: A B_SPLINE_SURFACE_WITH_KNOTS U knot vector contains two
consecutive interior knots equal in value (e.g. (0.0, 0.25, 0.25, 1.0))
while the multiplicity list claims multiplicity 1 at each side rather than a
single bumped multiplicity. Compliant readers should warn (and treat the pair
as a multiplicity-2 bump if it makes sense).

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS used as the face surface, degree (3,3),
    6x4 control net (6 CPs in U, 4 in V). U knot vector is
    (0.0, 0.25, 0.25, 1.0) with multiplicities (4,1,1,4) — sum = 10 =
    deg_u+nCP_u+1 = 3+6+1 = 10 ✓. The two interior knots are both 0.25,
    duplicated value, but each claims multiplicity 1. This is the unjustified
    duplicate knot defect: the parser sees two separate knots at the same
    parameter value, not a single knot at mult=2.
  - 3D edge curve on the bottom face edge: B_SPLINE_CURVE_WITH_KNOTS degree-2,
    6 CPs with a C-1 positional break at t=0.5 (CP[2]=(1.5,0,0) vs
    CP[3]=(3.0,0,0) — 1.5-unit gap). This forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: duplicated U interior knot at 0.25 with mult=1 each;
    parser accepts it, evaluation chokes or proceeds silently without diagnostic.
  - C-1 DRIVER: B-spline positional break at t=0.5 forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn001",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree (3,3) 6x4 net; "
        "U knots (0.0,0.25,0.25,1.0) mults (4,1,1,4) sum=10=3+6+1 — "
        "consecutive equal interior knots at 0.25 with mult=1 each (unjustified "
        "duplicate; should be single knot at mult=2 for C1, or no dup for C2); "
        "V knots well-formed (4,4) at (0.0,1.0); "
        "defect edge B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null=True"
    ),
)

# ── DEFECT SURFACE: B_SPLINE_SURFACE_WITH_KNOTS with duplicated U interior knot ──
# Control net: 6 rows (U) x 4 columns (V), degree (3,3).
# U: mults (4,1,1,4) sum=10, knots (0.0,0.25,0.25,1.0) — dup at 0.25 is the defect.
# V: mults (4,4) sum=8=3+4+1 ✓, knots (0.0,1.0) — well-formed Bezier strip.
p00 = f.cartesian_point((0.0, 0.0, 0.0));  p01 = f.cartesian_point((0.0, 1.0, 0.0))
p02 = f.cartesian_point((0.0, 2.0, 0.0));  p03 = f.cartesian_point((0.0, 3.0, 0.0))
p10 = f.cartesian_point((0.6, 0.0, 0.0));  p11 = f.cartesian_point((0.6, 1.0, 0.3))
p12 = f.cartesian_point((0.6, 2.0, 0.3));  p13 = f.cartesian_point((0.6, 3.0, 0.0))
p20 = f.cartesian_point((1.2, 0.0, 0.0));  p21 = f.cartesian_point((1.2, 1.0, 0.5))
p22 = f.cartesian_point((1.2, 2.0, 0.5));  p23 = f.cartesian_point((1.2, 3.0, 0.0))
# Interior dup knot at U=0.25: both CP rows at index 2 and 3 are at U~0.25
p30 = f.cartesian_point((1.8, 0.0, 0.0));  p31 = f.cartesian_point((1.8, 1.0, 0.5))
p32 = f.cartesian_point((1.8, 2.0, 0.5));  p33 = f.cartesian_point((1.8, 3.0, 0.0))
p40 = f.cartesian_point((2.4, 0.0, 0.0));  p41 = f.cartesian_point((2.4, 1.0, 0.3))
p42 = f.cartesian_point((2.4, 2.0, 0.3));  p43 = f.cartesian_point((2.4, 3.0, 0.0))
p50 = f.cartesian_point((3.0, 0.0, 0.0));  p51 = f.cartesian_point((3.0, 1.0, 0.0))
p52 = f.cartesian_point((3.0, 2.0, 0.0));  p53 = f.cartesian_point((3.0, 3.0, 0.0))

# Defect surface: U knot vector has two equal interior values at 0.25,
# both claiming mult=1. This is what the catalog documents as the bug.
# sum_u = 4+1+1+4 = 10 = 3+6+1 ✓ (structurally valid count, semantically broken)
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('dup_u_knot',3,3,"
    f"((#{p00.eid},#{p01.eid},#{p02.eid},#{p03.eid}),"
    f"(#{p10.eid},#{p11.eid},#{p12.eid},#{p13.eid}),"
    f"(#{p20.eid},#{p21.eid},#{p22.eid},#{p23.eid}),"
    f"(#{p30.eid},#{p31.eid},#{p32.eid},#{p33.eid}),"
    f"(#{p40.eid},#{p41.eid},#{p42.eid},#{p43.eid}),"
    f"(#{p50.eid},#{p51.eid},#{p52.eid},#{p53.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,1,1,4),(4,4),"
    f"(0.0,0.25,0.25,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

# ── Context edges (right, top, left) with proper pcurves ──
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((3.0, 0.0, 0.0))
p_c = f.cartesian_point((3.0, 3.0, 0.0))
p_d = f.cartesian_point((0.0, 3.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)


def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
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


e_right = mk_edge_with_pc(v_b, v_c, (3.0, 0.0, 0.0), (0., 1., 0.), 3.0, (3.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (3.0, 3.0, 0.0), (-1., 0., 0.), 3.0, (3.0, 3.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 3.0, 0.0), (0., -1., 0.), 3.0, (0.0, 3.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
# C-1 DRIVER: degree-2 B-spline with 1.5-unit positional gap at t=0.5.
# CP[2]=(1.5,0,0) → CP[3]=(3.0,0,0): 1.5-unit jump at the interior break.
# Knot vector (3,3,3) at (0.0,0.5,1.0): sum=9=2+6+1 ✓, two Bezier patches.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))   # end of first Bezier
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # start of second — 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((3.5,  0.0, 0.0))
dc5 = f.cartesian_point((3.0,  0.0, 0.0))   # snaps to face corner

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('dup_uknot_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# Pcurve for the defect edge (bottom: runs from U=0→3, V=0 on the surface)
pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.75, 0.0))
pp2 = f.cartesian_point((1.5,  0.0))
pp3 = f.cartesian_point((3.0,  0.0))
pp4 = f.cartesian_point((3.5,  0.0))
pp5 = f.cartesian_point((3.0,  0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('dup_uknot_c1_break_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('dup_uknot_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('dup_uknot_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('dup_uknot_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('dup_uknot_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
