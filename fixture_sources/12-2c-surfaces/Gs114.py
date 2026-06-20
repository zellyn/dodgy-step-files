"""Gs114 — B-spline surface with all control points coincident (degenerate point).

Catalog claim: B_SPLINE_SURFACE_WITH_KNOTS whose entire control net collapses to a
single 3D point; surface is a degenerate point rather than a patch.
ShapeAnalysis_Surface.IsDegenerated fails to detect this because it only checks
parameter-range extents, not 3D span of control points.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (all 4 control points = (0,0,0)) IS the
    ADVANCED_FACE.face_geometry; collapsed zero-span control net IS the mechanism
    wired into face topology; IsDegenerated() misses the collapse because it only
    tests parameter extents, not 3D control-point spread IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (all control points = (0,0,0))
    IS the ADVANCED_FACE.face_geometry; zero-span control net collapsing the
    surface to a single point IS the mechanism wired into face topology;
    IsDegenerated() parameter-extent test fails to detect 3D collapse IS the defect.
  - shape_null driver: degenerate point-surface; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs114",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (all control points = (0,0,0)) "
        "IS ADVANCED_FACE.face_geometry; "
        "zero-span control net collapsing surface to a single point IS "
        "the mechanism wired into face topology; "
        "IsDegenerated() parameter-extent test misses 3D collapse IS the defect; "
        "shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: all control points at origin ─────────────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# All 4 poles at (0,0,0) → zero 3D span → degenerate point surface.
ctrl_pts = [[f.cartesian_point((0.0, 0.0, 0.0)) for _ in range(2)] for _ in range(2)]
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(2)) + ")"
    for r in range(2)
) + ")"

bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs114_bss',1,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),"
    f"(0.0,1.0),"
    f"(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square in parameter space ─────────────────────────────
# All 3D corners map to (0,0,0) because all control points are coincident.
# The boundary encloses a valid parameter domain [0,1]×[0,1] but the surface
# is a degenerate point — every (u,v) maps to (0,0,0).
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((0.0, 0.0, 0.0))
p_C = f.cartesian_point((0.0, 0.0, 0.0))
p_D = f.cartesian_point((0.0, 0.0, 0.0))

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

# All 3D edges degenerate to zero-length segments at the origin.
# pcurves traverse the valid [0,1]×[0,1] parameter domain normally.
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 0.001,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
e1 = mk_edge_line(v_B, v_C,
                  (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 0.001,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
e2 = mk_edge_line(v_C, v_D,
                  (0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.001,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 0.0, 0.0), (0.0, -1.0, 0.0), 0.001,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS (all poles at origin) IS the face_geometry;
# zero-span control net IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
