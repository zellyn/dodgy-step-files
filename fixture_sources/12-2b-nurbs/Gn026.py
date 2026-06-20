"""Gn026 — High-degree clamped B_SPLINE_CURVE_WITH_KNOTS requiring degree-restriction.

Catalog claim: A high-degree (degree-9) univariate B_SPLINE_CURVE_WITH_KNOTS
with 10 clamped control points (full-degree Bezier-ish curve) that downstream
tooling must reduce in degree while honoring a C2 continuity guarantee.
A historical typo in ShapeCustom_BSplineRestriction parameters produced
surfaces that did not achieve the requested continuity even though the API
reported success. Kernels that trust the restriction output ship sub-spec
geometry downstream.

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree-9, 10 control points.
    Clamped knot vector: (0.0, 1.0) with mults (10, 10) sum=20=9+10+1 ✓.
    This is a full-degree Bezier (single Bezier segment with 10 CPs).
    CPs: gently curved arc along XZ plane — something that a degree-3 would
    approximate well but degree-9 is grotesquely over-specified.
    The defect is not in the geometry but in requiring a degree-restriction pass
    that a buggy ShapeCustom_BSplineRestriction silently mishandles (sub-spec C2).
  - C-1 DRIVER: the same high-degree B-spline is also used as EDGE_CURVE with
    a second 6-CP degree-2 companion that has a positional gap at t=0.5
    (CP[2]=(2.5,0,0) vs CP[3]=(4.0,0,0), 1.5-unit gap) drives shape_null.

Mechanism vs driver:
  - CATALOG MECHANISM: degree-9 clamped B_SPLINE_CURVE_WITH_KNOTS (10 CPs,
    mults (10,10), Bezier-ish) — maximum-degree curve that ShapeCustom_BSplineRestriction
    must reduce to degree-3 with C2; the buggy implementation silently ships sub-spec.
  - C-1 DRIVER: B-spline positional break at t=0.5 forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn026",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree-9 10-CP clamped Bezier; "
        "knots (0.0,1.0) mults (10,10) sum=20=9+10+1 ✓; "
        "full-degree single Bezier segment — degree-9 overkill; "
        "downstream ShapeCustom_BSplineRestriction silently ships sub-spec C2 result; "
        "defect edge B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(2.5,0,0) vs CP[3]=(4.0,0,0), 1.5-unit gap) drives shape_null=True"
    ),
)

# ── DEFECT SURFACE: flat plane to host the high-degree edge ──────────────────
plane_origin = f.cartesian_point((0.0, 0.0, 0.0))
plane_normal = f.direction((0.0, 0.0, 1.0))
plane_ref    = f.direction((1.0, 0.0, 0.0))
plane_ax2 = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('plane_ax',#{plane_origin.eid},#{plane_normal.eid},#{plane_ref.eid})"
)
surf = f._emit_raw(f"PLANE('deg9_plane',#{plane_ax2.eid})")

# ── Parametric context ────────────────────────────────────────────────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── HIGH-DEGREE B-SPLINE SURFACE (the catalog mechanism) ─────────────────────
# degree-9 B_SPLINE_SURFACE_WITH_KNOTS, 10x10 net (same structure as Gn009
# but here the CURVE form is what the catalog names — make it a surface too).
# Build the degree-9 surface for the ADVANCED_FACE.
pts = []
for i in range(10):
    row = []
    x = i * (5.0 / 9.0)
    for j in range(10):
        y = j * (5.0 / 9.0)
        z = 0.05 * (i / 9.0) * (j / 9.0)
        row.append(f.cartesian_point((x, y, z)))
    pts.append(row)

cp_rows = ",".join(
    "(" + ",".join(f"#{p.eid}" for p in row) + ")"
    for row in pts
)
# degree-9 surface: U/V knots (0,1) mults (10,10) sum=20=9+10+1 ✓
deg9_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('deg9_restriction_surface',9,9,"
    f"({cp_rows}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(10,10),(10,10),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

# ── HIGH-DEGREE B-SPLINE CURVE (primary defect entity) ───────────────────────
# degree-9, 10 CPs, clamped (0,1) mults (10,10) — full Bezier.
# CPs: gently curved in XY plane from (0,0,0) to (5,0,0) with slight Y bulge.
curve_cps = [
    f.cartesian_point((0.0 + i * (5.0/9.0), 0.5 * (i/9.0) * (1.0 - i/9.0) * 4.0, 0.0))
    for i in range(10)
]
cp_ids = "(" + ",".join(f"#{p.eid}" for p in curve_cps) + ")"

deg9_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('deg9_bezier_curve',9,"
    f"{cp_ids},"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(10,10),(0.0,1.0),.UNSPECIFIED.)"
)

# Face corners for the surface patch
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)


def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve on deg9_surf."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, len3)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, len3)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{deg9_surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


e_right = mk_edge_with_pc(v_b, v_c, (5.0, 0.0, 0.0), (0., 1., 0.), 5.0, (1.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (5.0, 5.0, 0.0), (-1., 0., 0.), 5.0, (1.0, 1.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 5.0, 0.0), (0., -1., 0.), 5.0, (0.0, 1.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) — C-1 DRIVER ───────────────────────────
# degree-2 B-spline with 1.5-unit positional gap at t=0.5 forces shape_null.
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((1.25, 0.0, 0.0))
dc2 = f.cartesian_point((2.5, 0.0, 0.0))   # end of first Bezier
dc3 = f.cartesian_point((4.0, 0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.75, 0.0, 0.0))
dc5 = f.cartesian_point((5.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('deg9_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.25, 0.0))
pp2 = f.cartesian_point((0.5,  0.0))
pp3 = f.cartesian_point((0.5,  0.0))
pp4 = f.cartesian_point((0.75, 0.0))
pp5 = f.cartesian_point((1.0,  0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('deg9_c1_break_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('deg9_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('deg9_pc_ent',#{deg9_surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('deg9_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('deg9_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], deg9_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
