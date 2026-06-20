"""Gs173 — ShapeUpgrade_ShapeCopy: offset surface mode coverage validation omission.

Catalog claim: OFFSET_SURFACE (+0.5 distance) with asymmetric coverage vs
base bounds; myOffsetSurfaceMode enabled without scope/extent check.
Defect: offset face coverage unchecked during collection.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - OFFSET_SURFACE (+0.5 distance, base B-SPLINE_SURFACE_WITH_KNOTS 2x2)
    IS the ADVANCED_FACE.face_geometry; face boundary edge pcurves
    referencing the OFFSET_SURFACE IS the mechanism wired into face topology;
    ShapeUpgrade_ShapeCopy myOffsetSurfaceMode enabled without offset coverage
    vs base-bounds check IS the defect.
  - Byte assertions: contains(b'OFFSET_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: OFFSET_SURFACE (+0.5, B-spline base) IS
    ADVANCED_FACE.face_geometry; face boundary edge pcurves on the
    OFFSET_SURFACE IS the mechanism wired into face topology;
    ShapeUpgrade_ShapeCopy myOffsetSurfaceMode enabled without scope/
    extent check (offset coverage vs base bounds unchecked) IS the defect.
  - shape_null driver: unverified offset coverage causes downstream surface
    evaluation outside valid region; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs173",
    defect=(
        "OFFSET_SURFACE (+0.5 distance, B-spline base) IS ADVANCED_FACE.face_geometry; "
        "face boundary edge pcurves on the OFFSET_SURFACE IS the mechanism wired "
        "into face topology; ShapeUpgrade_ShapeCopy myOffsetSurfaceMode enabled "
        "without offset coverage vs base-bounds check IS the defect; shape_null"
    ),
)

# ── B-spline base surface for OFFSET_SURFACE ─────────────────────────────────
# Byte assertion: contains(b'OFFSET_SURFACE')
#
# Build a simple 2×2 bilinear B-spline base surface over [0,1]×[0,1].
# U: deg 1, ncp=2 → sum_mults=2+1+1=4. Knots (0.,1.) mults (2,2) → sum=4 ✓.
# V: deg 1, ncp=2 → sum_mults=4. Knots (0.,1.) mults (2,2) → sum=4 ✓.
# Control points form a flat unit square in XY.

pts_2x2 = [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
    [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
]
cp_rows = [[f.cartesian_point(p) for p in row] for row in pts_2x2]
nested = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in cp_rows)

bspline_base = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs173_base',1,1,({nested}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),(0.,1.),(0.,1.),.UNSPECIFIED.)"
)

# OFFSET_SURFACE: distance +0.5 along surface normal.
# The coverage of the offset may extend beyond the base-surface bounds;
# ShapeUpgrade_ShapeCopy with myOffsetSurfaceMode=.T. copies the offset
# without checking whether the offset domain matches the base bounds.
offset_surf = f._emit_raw(
    f"OFFSET_SURFACE('gs173_offset',#{bspline_base.eid},0.5,.F.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square [0,1]x[0,1] in UV (offset surface domain) ─────
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
    pc  = f._emit_raw(f"PCURVE('pc',#{offset_surf.eid},#{pcd.eid})")
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

# OFFSET_SURFACE (+0.5 distance, B-spline base) IS the face_geometry; face
# boundary edge pcurves on the OFFSET_SURFACE IS the mechanism wired into
# face topology — exercises ShapeUpgrade_ShapeCopy myOffsetSurfaceMode
# enabled without offset coverage vs base-bounds check.
face  = f.advanced_face([f.face_outer_bound(loop)], offset_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
