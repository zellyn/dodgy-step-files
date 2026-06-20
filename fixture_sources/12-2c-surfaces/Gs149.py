"""Gs149 — IsUVBounded inverted trim bounds.

Catalog claim: ShapeAnalysis_Surface::IsUVBounded() checks whether a
trimmed B-spline surface reports bounded parametric status. When the
RECTANGULAR_TRIMMED_SURFACE carries inverted bounds (u1 > u2 or v1 > v2),
IsUVBounded may silently misclassify the surface as unbounded or crash the
bound-query path, producing incorrect topology decisions downstream.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (3x2 control grid, deg 2u/1v, knot domain
    [0,2.5]x[0,1]) wrapped in RECTANGULAR_TRIMMED_SURFACE with inverted
    U-bounds (u1=2.5, u2=0.5 — inverted) IS the ADVANCED_FACE.face_geometry;
    face boundary edge pcurve referencing the inverted U-trim interval IS
    the mechanism wired into face topology; IsUVBounded missing inverted-bound
    guard IS the defect.
  - Byte assertions: contains(b'RECTANGULAR_TRIMMED_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS wrapped in
    RECTANGULAR_TRIMMED_SURFACE with inverted U-bounds (u1=2.5 > u2=0.5)
    IS ADVANCED_FACE.face_geometry; face boundary edge pcurve at the
    inverted trim boundary IS the mechanism wired into face topology;
    IsUVBounded inverted-bound classification failure IS the defect.
  - shape_null driver: IsUVBounded returns wrong status; downstream bound
    queries use wrong range; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs149",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (deg 2u/1v, domain [0,2.5]x[0,1]) "
        "wrapped in RECTANGULAR_TRIMMED_SURFACE with inverted U-bounds "
        "(u1=2.5, u2=0.5 — u1>u2) IS ADVANCED_FACE.face_geometry; face "
        "boundary edge pcurve at inverted trim boundary IS the mechanism "
        "wired into face topology; IsUVBounded inverted-bound guard absence "
        "IS the defect; shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: 3x2 control grid, deg 2u/1v ─────────────────
# Byte assertion: contains(b'RECTANGULAR_TRIMMED_SURFACE')
# Degree 2 in U (3 ctrl pts, knots [0,1,2] mult [1,1,1] → domain [0,2]),
# Degree 1 in V (2 ctrl pts, knots [0,1] mult [1,1] → domain [0,1]).
# Scaled knots: U knots [0,1.25,2.5] → domain [0,2.5], V [0,1] → [0,1].
pts_3x2 = [
    # V=0 row
    [(0.0, 0.0, 0.0), (1.25, 0.0, 0.5), (2.5, 0.0, 0.0)],
    # V=1 row
    [(0.0, 1.0, 0.0), (1.25, 1.0, 0.5), (2.5, 1.0, 0.0)],
]
cp_rows = [[f.cartesian_point(p) for p in row] for row in pts_3x2]
nested = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in cp_rows)

bspline = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs149_bspline',2,1,({nested}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(1,1,1),(1,1),(0.,1.25,2.5),(0.,1.),.UNSPECIFIED.)"
)

# RECTANGULAR_TRIMMED_SURFACE with inverted U-bounds: u1=2.5, u2=0.5 (u1>u2)
# IsUVBounded must detect and reject these inverted bounds.
rts = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('gs149_rts',#{bspline.eid},2.5,0.5,0.2,0.8,.T.,.T.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary referencing the inverted RTS ────────────────────────────────
# The face edges use the RTS as their surface reference. The bottom edge pcurve
# starts at u=2.5 (the inverted upper bound) and sweeps to u=0.5 —
# this is the inverted-bound edge wired into the face topology.
# 3D corners approximate the surface at the trim corners.
p_A = f.cartesian_point((0.0, 0.2, 0.0))   # RTS corner u=0.5→mapped, v=0.2 (approx)
p_B = f.cartesian_point((2.5, 0.2, 0.0))   # u=2.5, v=0.2
p_C = f.cartesian_point((2.5, 0.8, 0.0))   # u=2.5, v=0.8
p_D = f.cartesian_point((0.0, 0.8, 0.0))   # u=0.5→mapped, v=0.8

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

# Bottom: A→B; pcurve from (u=2.5, v=0.2) to (u=0.5, v=0.2) — inverted U direction
# This IS the inverted-bound pcurve edge wired into face topology.
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.2, 0.0), (1.0, 0.0, 0.0), 2.5,
                  (2.5, 0.2), (-1.0, 0.0), 2.0)   # pcurve sweeps in -U (inverted bounds)
# Right: B→C, v=0.2→0.8 at u=2.5
e1 = mk_edge_line(v_B, v_C,
                  (2.5, 0.2, 0.0), (0.0, 1.0, 0.0), 0.6,
                  (2.5, 0.2), (0.0, 1.0), 0.6)
# Top: C→D, u=2.5→0.5 at v=0.8 (inverted)
e2 = mk_edge_line(v_C, v_D,
                  (2.5, 0.8, 0.0), (-1.0, 0.0, 0.0), 2.5,
                  (2.5, 0.8), (-1.0, 0.0), 2.0)
# Left: D→A, v=0.8→0.2 at u=0.5 (mapped)
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 0.8, 0.0), (0.0, -1.0, 0.0), 0.6,
                  (0.5, 0.8), (0.0, -1.0), 0.6)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RTS (wrapping B_SPLINE_SURFACE_WITH_KNOTS with inverted U-bounds u1>u2)
# IS the face_geometry; face boundary edge pcurve at inverted trim boundary
# IS the mechanism wired into face topology.
face  = f.advanced_face([f.face_outer_bound(loop)], rts)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
