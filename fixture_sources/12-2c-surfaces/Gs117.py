"""Gs117 — B-spline surface with pole count / knot-vector mismatch.

Catalog claim: B_SPLINE_SURFACE_WITH_KNOTS where the declared control-point
grid dimensions are inconsistent with the u-knot multiplicity sum
(n_poles_u ≠ sum_u_mults − degree − 1). OCCT's BSplineSurface constructor
silently truncates the pole grid rather than raising an error.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (degree=1, 3 poles in u, u-mults=(2,2,2)
    which requires 4 poles) IS the ADVANCED_FACE.face_geometry; pole/knot-count
    mismatch (3 poles declared, knot vector implies 4) IS the mechanism wired
    into face topology; BSplineSurface constructor silently truncates rather than
    rejecting IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (3 poles in u vs knot-vector
    requiring 4) IS the ADVANCED_FACE.face_geometry; pole/knot-count mismatch IS
    the mechanism wired into face topology; BSplineSurface silent truncation of
    pole grid IS the defect.
  - shape_null driver: mismatched pole/knot counts produce undefined surface;
    strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs117",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (3 poles in u, knot-vector requires 4) "
        "IS ADVANCED_FACE.face_geometry; "
        "pole/knot-count mismatch IS the mechanism wired into face topology; "
        "BSplineSurface silent truncation of pole grid IS the defect; "
        "shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: pole count mismatch ─────────────────────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# degree=1 in u; mults=(2,2,2) → sum=6 → requires n_poles_u = 6-1-1 = 4.
# But we declare only 3 poles in u → mismatch.
# 3 u-poles × 2 v-poles grid:
ctrl = [
    [(0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (1.0, 0.0, 0.0)],
    [(0.0, 1.0, 0.0), (0.5, 1.0, 0.0), (1.0, 1.0, 0.0)],
]
ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(3)) + ")"
    for r in range(2)
) + ")"

# mults=(2,2,2) sum=6 → expects 4 poles in u; only 3 declared → mismatch.
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs117_bss',1,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2,2),(2,2),"
    f"(0.0,0.5,1.0),"
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

# B_SPLINE_SURFACE_WITH_KNOTS (pole/knot-count mismatch) IS the face_geometry;
# underdeclared pole grid IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
