"""Gs142 — Segment rational-weight singularity.

Catalog claim: Segment() subdivides rational B-spline surfaces without
validating weight stability across split boundaries. For mixed-weight
surfaces, splitting at a critical parameter can create false singularities
where weight transitions occur at patch edge. Boundary evaluation becomes
unstable.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (rational, mixed weights including near-zero
    weight at the split boundary) IS the ADVANCED_FACE.face_geometry; face
    edge 3D curve lies at the critical split parameter where weight transitions
    to near-zero IS the mechanism wired into face topology; Segment() missing
    weight-stability validation at split boundary IS the defect.
  - Byte assertions: contains(b'RATIONAL_B_SPLINE_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: rational B-spline surface IS ADVANCED_FACE.face_geometry;
    face boundary edge at the critical split parameter where weight drops to
    near-zero IS the mechanism wired into face topology; Segment()
    weight-stability validation absence at split boundary IS the defect.
  - shape_null driver: false singularity at split boundary; unstable weight
    evaluation; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs142",
    defect=(
        "Rational B-spline surface (mixed weights, near-zero at split boundary) "
        "IS ADVANCED_FACE.face_geometry; face boundary edge at critical split "
        "parameter where weight transitions to near-zero IS the mechanism wired "
        "into face topology; Segment() weight-stability validation absence IS "
        "the defect; shape_null"
    ),
)

# ── Rational B-spline surface with mixed weights ───────────────────────────────
# Byte assertion: contains(b'RATIONAL_B_SPLINE_SURFACE')
# Degree 2x2, 3x3 control grid.
# Weights: most weights = 1.0, but at the split boundary column (u=mid)
# weight drops to near-zero (1e-6), creating a false singularity when
# Segment() splits at that critical parameter.
#
# Control grid: 3 rows x 3 cols
pts_3x3 = [
    [(0.0, 0.0, 0.0), (1.0, 0.0, 1.0), (2.0, 0.0, 0.0)],
    [(0.0, 1.0, 0.0), (1.0, 1.0, 1.0), (2.0, 1.0, 0.0)],
    [(0.0, 2.0, 0.0), (1.0, 2.0, 1.0), (2.0, 2.0, 0.0)],
]
cp_rows = [[f.cartesian_point(p) for p in row] for row in pts_3x3]
nested = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in cp_rows)

# Weights: column 1 (the middle, split-boundary column) has weight 1e-6
# Weight array must be LIST OF LIST matching control point grid order (rows x cols)
# Row 0: (1.0, 1e-6, 1.0), Row 1: (1.0, 1e-6, 1.0), Row 2: (1.0, 1e-6, 1.0)
w_normal = 1.0
w_singular = "1.0e-6"
weights = (
    f"(({w_normal},{w_singular},{w_normal}),"
    f"({w_normal},{w_singular},{w_normal}),"
    f"({w_normal},{w_singular},{w_normal}))"
)

# B_SPLINE_SURFACE_WITH_KNOTS + RATIONAL_B_SPLINE_SURFACE complex entity
bspline = f._emit_raw(
    f"(B_SPLINE_SURFACE(2,2,({nested}),.UNSPECIFIED.,.F.,.F.,.F.)"
    f"B_SPLINE_SURFACE_WITH_KNOTS((1,1,1),(1,1,1),(0.,1.,2.),(0.,1.,2.),.UNSPECIFIED.)"
    f"GEOMETRIC_REPRESENTATION_ITEM()"
    f"RATIONAL_B_SPLINE_SURFACE({weights})"
    f"REPRESENTATION_ITEM('gs142_rational_bspline')"
    f"SURFACE())"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: edge at the critical split parameter u=1.0 ─────────────────
# The split boundary is at u=1.0 (middle knot) where weight = 1e-6.
# The face left and right boundary edges run along u=0 and u=2 (normal weight),
# but the top/bottom edges cross through u=1.0 (the split-boundary singularity).
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

# Bottom: A→B crossing through u=1 (split boundary with near-zero weight)
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 2.0,
                  (0.0, 0.0), (1.0, 0.0), 2.0)
# Right: B→C (v: 0→2 at u=2, normal weight)
e1 = mk_edge_line(v_B, v_C,
                  (2.0, 0.0, 0.0), (0.0, 1.0, 0.0), 2.0,
                  (2.0, 0.0), (0.0, 1.0), 2.0)
# Top: C→D crossing through u=1 (split boundary with near-zero weight)
e2 = mk_edge_line(v_C, v_D,
                  (2.0, 2.0, 0.0), (-1.0, 0.0, 0.0), 2.0,
                  (2.0, 2.0), (-1.0, 0.0), 2.0)
# Left: D→A (v: 2→0 at u=0, normal weight)
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 2.0, 0.0), (0.0, -1.0, 0.0), 2.0,
                  (0.0, 2.0), (0.0, -1.0), 2.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# Rational B-spline IS the face_geometry; face boundary crossing the near-zero
# weight split-boundary IS the mechanism wired into face topology.
face  = f.advanced_face([f.face_outer_bound(loop)], bspline)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
