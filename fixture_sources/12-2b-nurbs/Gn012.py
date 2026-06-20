"""Gn012 — C0 BSpline curves should be split into C1+ pieces.

Catalog claim: BSpline curves whose interior knot multiplicities equal their
degree introduce true C0 joins (slope/tangent discontinuities). Downstream
tools requiring at least C1 fail. The healer should split at C0 points so each
piece is at least C1.

OCC behavior: silently accepts (no diagnostic, empty result).
Tier-3 assertion: load == "ok" (shape_null == False).
Expected: occt=shape(1) — the defect is that OCC loads it without healing
(no diagnostic, no split into C1 pieces). The shape loads but the C0 break
is silently accepted.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 3, 7 control points.
    Knot vector: (0.0, 0.5, 1.0) with mults (4, 3, 4).
    sum = 4+3+4 = 11 = 3+7+1 = 11 ✓.
    Interior knot at t=0.5 has multiplicity 3 = degree, producing a C0 join
    (continuity = degree - multiplicity = 3 - 3 = 0). This is the catalog
    mechanism: a genuine C0 tangent break inside the curve.
  - CPs: first half curves up to (1.5, 1.5, 0) then second half goes to (3, 0, 0),
    with a sharp tangent break at the interior join.
  - NO C-1 driver: tier-3 assertion is load=="ok" (shape_null False), so we
    want OCC to accept this. The defect is silent acceptance without healing.

Mechanism vs driver:
  - CATALOG MECHANISM: interior knot multiplicity = degree (mult=3, deg=3)
    at t=0.5 → C0 join. A compliant kernel would split at this point.
  - NO C-1 DRIVER needed: catalog expects shape(1), so we let OCC accept it.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn012",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree-3, 7 CPs; "
        "knots (0.0,0.5,1.0) mults (4,3,4) sum=11=3+7+1 ✓; "
        "interior multiplicity=degree=3 at t=0.5 → C0 join (tangent break); "
        "first segment rises to (1.5,1.5,0), second descends to (3,0,0); "
        "healer should split into two C1+ pieces; OCC silently accepts without split"
    ),
)

# Host surface: a plane so the face infrastructure is valid
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners: rectangle [0,3] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((3.0, 0.0, 0.0))
p_c = f.cartesian_point((3.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
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


e_right = mk_edge_with_pc(v_b, v_c, (3.0, 0.0, 0.0), (0., 1., 0.), 2.0, (3.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (3.0, 2.0, 0.0), (-1., 0., 0.), 3.0, (3.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) — THE CATALOG MECHANISM ─────────────────
# B_SPLINE_CURVE_WITH_KNOTS degree-3, 7 CPs.
# Interior knot at t=0.5 with mult=3 = degree → C0 join (tangent break).
# First half: (0,0,0) → (0.5,1,0) → (1,1.5,0) → (1.5,1.5,0) (tangent right)
# Second half: (1.5,1.5,0) → (1.5,1.0,0) → (2.0,0.5,0) → (3,0,0) (tangent down-right)
# The sharp change in tangent direction at CP[3]=(1.5,1.5,0) is the C0 break.

dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((0.5, 1.0, 0.0))
dc2 = f.cartesian_point((1.0, 1.5, 0.0))
dc3 = f.cartesian_point((1.5, 1.5, 0.0))   # C0 join point: left tangent ≠ right tangent
dc4 = f.cartesian_point((1.5, 1.0, 0.0))   # right side starts going down
dc5 = f.cartesian_point((2.0, 0.5, 0.0))
dc6 = f.cartesian_point((3.0, 0.0, 0.0))

# Degree 3, 7 CPs, interior mult=3 at t=0.5 → C0 join
# mults (4,3,4) sum=11=3+7+1 ✓
bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('c0_join_curve',3,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid},#{dc6.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,3,4),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# Pcurve: linear from (0,0) to (3,0) in UV
pp_s = f.cartesian_point((0.0, 0.0))
d2e  = f.direction((1., 0.))
v2   = f.vector(d2e, 3.0)
l2   = f.line(pp_s, v2)
pcd  = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('c0_join_pc_def',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('c0_join_pc_ent',#{surf.eid},#{pcd.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('c0_join_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('c0_join_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
