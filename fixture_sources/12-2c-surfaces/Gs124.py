"""Gs124 — B-SPLINE_SURFACE with u_periodic flag but non-coincident poles.

Catalog claim: ShapeAnalysis_Surface.IsUClosed reports true based on the
u_periodic flag, but the first/last U-poles don't coincide, leaving a gap.
This confuses healing logic which expects closed surfaces to have geometrically
coincident boundaries.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (u_closed=.T., u-poles at u=0 offset from
    u=1 poles by (0.2, 0.0, 0.0), non-coincident first/last column) IS the
    ADVANCED_FACE.face_geometry; u_periodic flag set but first/last U-poles
    geometrically non-coincident IS the mechanism wired into face topology;
    IsUClosed trusting periodic flag without geometric pole check IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (u_closed=.T. flag, but
    first U-column at x=0.0 and last U-column at x=1.2 — a 0.2-unit gap)
    IS the ADVANCED_FACE.face_geometry; flag-geometry mismatch for U-closure
    IS the mechanism wired into face topology; IsUClosed flag-only trust
    without geometric validation IS the defect.
  - shape_null driver: gap in nominally closed surface causes topology/geometry
    inconsistency; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs124",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (u_closed=.T. flag, first U-column at x=0.0, "
        "last U-column at x=1.2, 0.2-unit gap) IS ADVANCED_FACE.face_geometry; "
        "u_periodic flag set but first/last U-poles non-coincident "
        "IS the mechanism wired into face topology; "
        "IsUClosed flag-only trust without geometric pole coincidence check "
        "IS the defect; shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: u_closed=.T. but non-coincident poles ────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# degree=1 in u and v; 4 poles in u (first col x=0.0, last col x=1.2 → gap=0.2)
# u_closed flag = .T. (should mean first/last columns coincide, but they don't)
# mults=(2,1,1,2) sum=6 → n_poles_u = 6-1-1 = 4 ✓
# mults=(2,2) sum=4 → n_poles_v = 4-1-1 = 2 ✓
ctrl = [
    [(0.0, 0.0, 0.0), (0.4, 0.0, 0.0), (0.8, 0.0, 0.0), (1.2, 0.0, 0.0)],
    [(0.0, 1.0, 0.0), (0.4, 1.0, 0.0), (0.8, 1.0, 0.0), (1.2, 1.0, 0.0)],
]
ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(4)) + ")"
    for r in range(2)
) + ")"

# u_closed = .T. (third positional boolean after v_closed)
# B_SPLINE_SURFACE_WITH_KNOTS(name, u_degree, v_degree, control_pts,
#   surface_form, u_closed, v_closed, self_intersect, u_mults, v_mults,
#   u_knots, v_knots, knot_spec)
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs124_bss',1,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.T.,.F.,.F.,"
    f"(2,1,1,2),(2,2),"
    f"(0.0,0.333,0.667,1.0),"
    f"(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square in parameter space ─────────────────────────────
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((1.0, 0.0, 0.0))
p_C = f.cartesian_point((1.0, 1.0, 0.0))
p_D = f.cartesian_point((0.0, 1.0, 0.0))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{bss.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 1.0, 0.0), (-1.0, 0.0, 0.0), 1.0,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS (u_closed=.T. but non-coincident first/last
# U-poles) IS the face_geometry; flag/geometry mismatch IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
