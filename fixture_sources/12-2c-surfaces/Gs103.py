"""Gs103 — IsUClosed: periodic-vs-closed semantic mismatch.

Catalog claim: Surface IsUClosed() checks u_closed declaration flag, not actual
geometry. Surface may declare u_closed=true but control polygon doesn't close
within tolerance (gap > Precision::Confusion).

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS declared with .T. (u_closed=true) but whose
    first and last u-column of control poles differ by 0.1 (gap > tolerance)
    IS the ADVANCED_FACE.face_geometry; face boundary spans full u-period
    [0,2π] relying on declared closure IS the mechanism wired into face
    topology; IsUClosed() returns true based on declaration flag while
    geometry is open IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (u_closed=.T.) IS the
    ADVANCED_FACE.face_geometry; u-column gap of 0.1 between first and last
    pole violates declared closure IS the mechanism wired into face topology;
    IsUClosed() trusts declaration flag over geometry IS the defect.
  - shape_null driver: closed-flag/geometry mismatch; strict kernels reject;
    empty result.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs103",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (u_closed=.T.) IS ADVANCED_FACE.face_geometry; "
        "u-column gap of 0.1 between first and last pole violates declared closure "
        "IS the mechanism wired into face topology; "
        "IsUClosed() trusts declaration flag over geometry IS the defect; shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: u_closed=.T. but first/last u-poles differ ───
# Degree 1 in u (3 knots: 0,1,2 with mult 2,1,2), degree 1 in v.
# First u-column z=0.0, last u-column z=0.1 — gap 0.1 > Precision::Confusion.
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
ctrl = [
    # u=0 row: z=0.0          u=1 row: z=0.05        u=2 row: z=0.1 (gap!)
    [(0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (1.0, 0.0, 0.1)],
    [(0.0, 1.0, 0.0), (0.5, 1.0, 0.0), (1.0, 1.0, 0.1)],
]
ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(3)) + ")"
    for r in range(2)
) + ")"

bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs103_bss',1,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.T.,.F.,.F.,"
    f"(2,1,2),(2,2),"
    f"(0.0,1.0,2.0),"
    f"(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: rectangle on [0,2]×[0,1] parameter domain ─────────────────
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((1.0, 0.0, 0.1))
p_C = f.cartesian_point((1.0, 1.0, 0.1))
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

# e0: bottom A→B (v=0, u: 0→2)
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.1), math.sqrt(1.0 + 0.01),
                  (0.0, 0.0), (1.0, 0.0), 2.0)
# e1: right B→C (u=2, v: 0→1)
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.1), (0.0, 1.0, 0.0), 1.0,
                  (2.0, 0.0), (0.0, 1.0), 1.0)
# e2: top C→D (v=1, u: 2→0)
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 1.0, 0.1), (-1.0, 0.0, -0.1), math.sqrt(1.0 + 0.01),
                  (2.0, 1.0), (-1.0, 0.0), 2.0)
# e3: left D→A (u=0, v: 1→0)
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS (u_closed=.T.) IS the face_geometry;
# u-column gap IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
