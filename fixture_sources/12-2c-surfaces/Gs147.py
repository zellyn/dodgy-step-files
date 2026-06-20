"""Gs147 — ValueOfUV projection beyond bound.

Catalog claim: ShapeAnalysis_Surface::ValueOfUV() projects a 3D point onto
a surface and returns parametric (u,v). When the projection falls outside
the natural surface parameter range (e.g., a point beyond the B-spline
knot domain), the code silently clamps or returns unclamped values without
reporting out-of-bounds. Downstream operations receive wrong u/v, breaking
edge-surface topology.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (knot domain [0,2]x[0,2]) IS the
    ADVANCED_FACE.face_geometry; face boundary edge pcurve carries a
    parametric point at u=3.0 (beyond knot domain [0,2]) IS the mechanism
    wired into face topology; ValueOfUV out-of-bounds clamping without
    confidence flag IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (domain [0,2]x[0,2])
    IS ADVANCED_FACE.face_geometry; face boundary edge pcurve referencing
    parametric coordinate u=3.0 (outside knot domain) IS the mechanism
    wired into face topology; ValueOfUV silent out-of-bounds clamping IS
    the defect.
  - shape_null driver: wrong u/v returned; edge-surface mapping broken;
    strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs147",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (knot domain [0,2]x[0,2]) "
        "IS ADVANCED_FACE.face_geometry; face boundary edge pcurve with "
        "parametric endpoint u=3.0 (outside knot domain [0,2]) IS the "
        "mechanism wired into face topology; ValueOfUV silent out-of-bounds "
        "clamping without confidence flag IS the defect; shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: domain [0,2]x[0,2] ──────────────────────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# Degree 2x2, 3x3 control points, knots [0,1,2] multiplicities [1,1,1].
# Natural parameter domain: u in [0,2], v in [0,2].
# The face pcurve will reference u=3.0 — outside the domain — triggering
# ValueOfUV's silent clamp or unclamped return.
pts_3x3 = [
    [(0.0, 0.0, 0.0), (1.0, 0.0, 0.5), (2.0, 0.0, 0.0)],
    [(0.0, 1.0, 0.5), (1.0, 1.0, 1.0), (2.0, 1.0, 0.5)],
    [(0.0, 2.0, 0.0), (1.0, 2.0, 0.5), (2.0, 2.0, 0.0)],
]
cp_rows = [[f.cartesian_point(p) for p in row] for row in pts_3x3]
nested = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in cp_rows)

bspline = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs147_bspline',2,2,({nested}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(1,1,1),(1,1,1),(0.,1.,2.),(0.,1.,2.),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary with out-of-bounds pcurve parameter ─────────────────────────
# The face boundary nominally spans the domain [0,2]x[0,2], but the bottom
# edge pcurve starts at u=3.0 — outside the knot domain [0,2].
# This is the u/v mapping inconsistency that triggers ValueOfUV clamping.
# 3D corners use the surface evaluation at u=2 (clamped boundary):
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((2.0, 0.0, 0.0))
p_C = f.cartesian_point((2.0, 2.0, 0.0))
p_D = f.cartesian_point((0.0, 2.0, 0.0))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{bspline.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Bottom: A→B, 3D: u=0→2 at v=0, but pcurve starts at u=3.0 (out-of-bounds)
# The pcurve direction sweeps from u=3.0 toward u=5.0 — entirely beyond domain.
# This IS the out-of-bounds parametric mapping wired into the face boundary.
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 2.0,
                  (3.0, 0.0), (1.0, 0.0), 2.0)   # pcurve u starts at 3.0 (outside [0,2])
# Right: B→C, u=2 at v=0→2 (normal)
e1 = mk_edge_line(v_B, v_C,
                  (2.0, 0.0, 0.0), (0.0, 1.0, 0.0), 2.0,
                  (2.0, 0.0), (0.0, 1.0), 2.0)
# Top: C→D, u=2→0 at v=2 (normal)
e2 = mk_edge_line(v_C, v_D,
                  (2.0, 2.0, 0.0), (-1.0, 0.0, 0.0), 2.0,
                  (2.0, 2.0), (-1.0, 0.0), 2.0)
# Left: D→A, u=0 at v=2→0 (normal)
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 2.0, 0.0), (0.0, -1.0, 0.0), 2.0,
                  (0.0, 2.0), (0.0, -1.0), 2.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry; face boundary edge with
# pcurve at u=3.0 (outside knot domain [0,2]) IS the mechanism wired into
# face topology (triggers ValueOfUV out-of-bounds silent clamp).
face  = f.advanced_face([f.face_outer_bound(loop)], bspline)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
