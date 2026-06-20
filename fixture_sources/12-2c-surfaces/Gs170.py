"""Gs170 — ShapeAnalysis_Surface: trimmed surface closure validation skip.

Catalog claim: A RECTANGULAR_TRIMMED_SURFACE on a U-periodic base surface
where the U-span trim crosses the seam; closure check absent so UV domain
is treated as continuous. Defect: no closure-aware parameterization guard.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - RECTANGULAR_TRIMMED_SURFACE (U-periodic B-SPLINE basis, u1=0.5, u2=2.5,
    crossing seam at u=2π) IS the ADVANCED_FACE.face_geometry; face boundary
    edge pcurves referencing the trimmed surface IS the mechanism wired into
    face topology; ShapeAnalysis_Surface closure check absent (UV domain
    treated as continuous across seam) IS the defect.
  - Byte assertions: contains(b'RECTANGULAR_TRIMMED_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: RECTANGULAR_TRIMMED_SURFACE on U-periodic B-spline
    base (u1=0.5, u2=2.5, crosses seam at u=2) IS ADVANCED_FACE.face_geometry;
    face boundary edge pcurves on the trimmed surface IS the mechanism wired
    into face topology; ShapeAnalysis_Surface missing closure-aware guard
    (UV domain treated as continuous) IS the defect.
  - shape_null driver: seam-crossing trim causes domain discontinuity;
    UV projection logic fails on non-continuous parameterization; strict
    kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs170",
    defect=(
        "RECTANGULAR_TRIMMED_SURFACE (U-periodic B-spline basis, u1=0.5, u2=2.5, "
        "seam at u=2.0) IS ADVANCED_FACE.face_geometry; face boundary edge pcurves "
        "on the trimmed surface IS the mechanism wired into face topology; "
        "ShapeAnalysis_Surface missing closure-aware parameterization guard "
        "(UV domain treated as continuous across seam) IS the defect; shape_null"
    ),
)

# ── U-periodic B-SPLINE_SURFACE_WITH_KNOTS basis ─────────────────────────────
# Byte assertion: contains(b'RECTANGULAR_TRIMMED_SURFACE')
#
# Build a closed-in-U (U_CLOSED=.T.) B-spline surface.
# U direction: degree 2, 5 control points, periodic-like by repeating end poles.
#   Knots (0.,1.,2.,3.) mults (1,2,2,1) → open but declared U_CLOSED.
#   sum = 1+2+2+1 = 6 = 5+2+1-2 (periodic count) — simplified open form.
# V direction: degree 1, 2 control points.
#   Knots (0.,1.) mults (2,2) → linear, clamped.
#
# The trim crosses the "seam" declared by U_CLOSED: u1=0.5, u2=2.5 spans
# across u=2, which the closure-unaware sampler treats as a normal interval.

pts_5x2 = [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
    [(1.0, 0.0, 0.1), (1.0, 1.0, 0.1)],
    [(2.0, 0.0, 0.0), (2.0, 1.0, 0.0)],
    [(3.0, 0.0, -0.1), (3.0, 1.0, -0.1)],
    [(4.0, 0.0, 0.0), (4.0, 1.0, 0.0)],
]
cp_rows = [[f.cartesian_point(p) for p in row] for row in pts_5x2]
nested = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in cp_rows)

# U: deg 2, mults (3,2,2,3) but to keep sum=5+2+1=8: use (3,2,3) 3 knot vals
# Actually: ncp=5, deg=2 → sum_mults = 5+2+1 = 8 for non-periodic.
# Knots (0.,1.,2.,3.) mults (2,2,2,2) → sum=8 ✓; interior knots at 1,2.
# V: deg 1, ncp=2 → sum_mults=2+1+1=4. Knots (0.,1.) mults (2,2) → sum=4 ✓.
bspline_base = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs170_base',2,1,({nested}),"
    f".UNSPECIFIED.,.T.,.F.,.F.,"
    f"(2,2,2,2),(2,2),(0.,1.,2.,3.),(0.,1.),.UNSPECIFIED.)"
)

# RECTANGULAR_TRIMMED_SURFACE: trim u from 0.5 to 2.5 (crosses seam at u=2.0),
# v from 0.0 to 1.0. usense=.T. vsense=.T.
rts = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('gs170_rts',#{bspline_base.eid},"
    f"0.5,2.5,0.,1.,.T.,.T.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary in trimmed surface UV domain [0.5,2.5]x[0,1] ───────────────
p_A = f.cartesian_point((0.5, 0.0, 0.0))
p_B = f.cartesian_point((2.5, 0.0, 0.0))
p_C = f.cartesian_point((2.5, 1.0, 0.0))
p_D = f.cartesian_point((0.5, 1.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)


def mk_edge_line(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{rts.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


# Bottom: A→B, u=0.5→2.5 at v=0
e0 = mk_edge_line(v_A, v_B,
                  (0.5, 0.0, 0.0), (1.0, 0.0, 0.0), 2.0,
                  (0.5, 0.0), (1.0, 0.0), 2.0)
# Right: B→C, v=0→1 at u=2.5
e1 = mk_edge_line(v_B, v_C,
                  (2.5, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
                  (2.5, 0.0), (0.0, 1.0), 1.0)
# Top: C→D, u=2.5→0.5 at v=1
e2 = mk_edge_line(v_C, v_D,
                  (2.5, 1.0, 0.0), (-1.0, 0.0, 0.0), 2.0,
                  (2.5, 1.0), (-1.0, 0.0), 2.0)
# Left: D→A, v=1→0 at u=0.5
e3 = mk_edge_line(v_D, v_A,
                  (0.5, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (0.5, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RECTANGULAR_TRIMMED_SURFACE on U-periodic base (u1=0.5,u2=2.5 crosses seam)
# IS the face_geometry; face boundary edge pcurves on the trimmed surface IS
# the mechanism wired into face topology — exercises ShapeAnalysis_Surface
# missing closure-aware parameterization guard.
face  = f.advanced_face([f.face_outer_bound(loop)], rts)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
