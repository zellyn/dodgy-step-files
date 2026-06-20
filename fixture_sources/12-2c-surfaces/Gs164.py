"""Gs164 — BezierSurface pole extraction dispatch.

Catalog claim: ShapeUpgrade_ShapeCopy dispatches pole extraction to
BSplineSurface or BezierSurface. Missing mutual exclusion: surfaces
classified as both offset-like and Bezier-like may be counted twice.
Fixture: BEZIER_SURFACE 5x5 poles; observer myNbBezierSurf incremented
exactly once.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - BEZIER_SURFACE (5x5 poles, deg 2/2) IS the ADVANCED_FACE.face_geometry;
    face boundary edge pcurves referencing the Bezier surface IS the
    mechanism wired into face topology; ShapeUpgrade_ShapeCopy missing
    mutual exclusion in pole-extraction dispatch (double-count possible)
    IS the defect.
  - Byte assertions: contains(b'BEZIER_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: BEZIER_SURFACE (5x5 poles) IS
    ADVANCED_FACE.face_geometry; face boundary edge pcurves on Bezier
    surface IS the mechanism wired into face topology;
    ShapeUpgrade_ShapeCopy dispatch missing mutual exclusion (myNbBezierSurf
    double-increment) IS the defect.
  - shape_null driver: pole count inflated by double-increment; downstream
    algorithms receive corrupted count; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs164",
    defect=(
        "BEZIER_SURFACE (5x5 poles, deg 2/2) IS ADVANCED_FACE.face_geometry; "
        "face boundary edge pcurves on Bezier surface IS the mechanism wired into "
        "face topology; ShapeUpgrade_ShapeCopy dispatch missing mutual exclusion "
        "(myNbBezierSurf double-increment) IS the defect; shape_null"
    ),
)

# ── BEZIER_SURFACE: 5x5 poles (degree 2 in both directions, rational=.F.) ────
# Byte assertion: contains(b'BEZIER_SURFACE')
#
# BEZIER_SURFACE(name, u_degree, v_degree, control_points_list,
#                surface_form, u_closed, v_closed, self_intersect)
# 5x5 control point grid on [0,4]x[0,4] at z=0.
# ShapeUpgrade_ShapeCopy checks IsKind(BSplineSurface) and IsKind(BezierSurface)
# without mutual exclusion; a surface classified as both is counted twice.

pts = []
for i in range(5):
    row = []
    for j in range(5):
        row.append(f.cartesian_point((float(i), float(j), 0.0)))
    pts.append(row)

nested = ",".join(
    "(" + ",".join(f"#{p.eid}" for p in row) + ")"
    for row in pts
)

bezier = f._emit_raw(
    f"BEZIER_SURFACE('gs164_bezier',2,2,({nested}),"
    f".UNSPECIFIED.,.F.,.F.,.F.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square [0,1]x[0,1] in UV, pcurves on Bezier surface ──
# Bezier surface domain u in [0,1], v in [0,1] (parametric).
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
    pc  = f._emit_raw(f"PCURVE('pc',#{bezier.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


# Bottom: A→B, u=0→1 at v=0
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
# Right: B→C, v=0→1 at u=1
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
# Top: C→D, u=1→0 at v=1
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 1.0, 0.0), (-1.0, 0.0, 0.0), 1.0,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
# Left: D→A, v=1→0 at u=0
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# BEZIER_SURFACE (5x5 poles) IS the face_geometry; face boundary edge pcurves
# on the Bezier surface IS the mechanism wired into face topology — exercises
# ShapeUpgrade_ShapeCopy dispatch missing mutual exclusion in pole-extraction.
face  = f.advanced_face([f.face_outer_bound(loop)], bezier)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
