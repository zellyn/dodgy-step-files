"""Gs144 — ComputeBoxes null-ISO silent skip.

Catalog claim: ShapeAnalysis_Surface::ComputeBoxes() iterates U and V
iso-curves to build a bounding box. When a surface has a degenerate patch
(zero-length iso-curve at one parametric boundary), the null iso-curve is
silently skipped via lazy-null-guard, leaving BndLib_Add3dCurve::Add
uncalled for that edge. The resulting bounding box omits that facet.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (degenerate: top V-row collapses all U
    control points to a single point, creating a null V-max iso-curve)
    IS the ADVANCED_FACE.face_geometry; face boundary edge along the
    degenerate V-max iso-curve (null iso, zero length) IS the mechanism
    wired into face topology; ComputeBoxes null-ISO silent skip IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (degenerate top V-row
    collapsing to a single apex point) IS ADVANCED_FACE.face_geometry; face
    boundary edge at degenerate V-max row (null iso-curve) IS the mechanism
    wired into face topology; ComputeBoxes null-ISO silent skip IS the defect.
  - shape_null driver: incomplete bounding box from null-iso skip; downstream
    interference checks miss facets; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs144",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (degenerate: top V-row collapses all U "
        "control points to single apex point, producing null V-max iso-curve) "
        "IS ADVANCED_FACE.face_geometry; face boundary edge at degenerate V-max "
        "iso-curve (null iso) IS the mechanism wired into face topology; "
        "ComputeBoxes null-ISO silent skip IS the defect; shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: degenerate top V-row ─────────────────────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# Degree 2x2, 3x3 control grid.
# All top V-row (row index 2) control points collapse to a single apex point
# (0,0,2). This makes the V=1.0 iso-curve degenerate (zero-length, null ISO).
# ComputeBoxes iterates iso-curves; the null iso at V-max triggers the skip.
pts_3x3 = [
    # Bottom row (V=0): normal spread
    [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (2.0, 0.0, 0.0)],
    # Middle row (V=0.5): lifted
    [(0.0, 1.0, 1.0), (1.0, 1.0, 1.5), (2.0, 1.0, 1.0)],
    # Top row (V=1): ALL collapsed to single apex point — null iso-curve
    [(1.0, 2.0, 2.0), (1.0, 2.0, 2.0), (1.0, 2.0, 2.0)],
]
cp_rows = [[f.cartesian_point(p) for p in row] for row in pts_3x3]
nested = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in cp_rows)

bspline = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs144_degenerate',2,2,({nested}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(1,1,1),(1,1,1),(0.,1.,2.),(0.,1.,2.),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary ──────────────────────────────────────────────────────────────
# Three distinct corners: A (bottom-left), B (bottom-right), apex C (top).
# The bottom edge A→B is a normal iso-curve at V=0.
# The two side edges B→C and C→A converge to the apex — this is the boundary
# that exercises the null V-max iso-curve at runtime.
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((2.0, 0.0, 0.0))
p_C = f.cartesian_point((1.0, 2.0, 2.0))  # apex (degenerate top)

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)

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

# Bottom: A→B, u=0→2 at v=0 (normal iso-curve, full width)
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 2.0,
                  (0.0, 0.0), (1.0, 0.0), 2.0)
# Right side: B→C, converging to apex (exercises degenerate V-max iso)
e1 = mk_edge_line(v_B, v_C,
                  (2.0, 0.0, 0.0), (-1.0, 2.0, 2.0), 3.0,
                  (2.0, 0.0), (-1.0, 1.0), 2.0)
# Left side: C→A, from apex back to bottom-left
e2 = mk_edge_line(v_C, v_A,
                  (1.0, 2.0, 2.0), (-1.0, -2.0, -2.0), 3.0,
                  (1.0, 2.0), (-1.0, -1.0), 2.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS (degenerate top V-row) IS the face_geometry;
# face boundary edge converging to degenerate apex IS the mechanism wired
# into face topology (exercises null V-max iso-curve in ComputeBoxes).
face  = f.advanced_face([f.face_outer_bound(loop)], bspline)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
