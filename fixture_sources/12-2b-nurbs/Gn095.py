"""Gn095 — ShapeUpgrade_ConvertSurfaceToBezierBasis 1x1-control-grid.

Catalog claim: Degenerate B-spline surface with only 1 control point (collapsed
to a single point); converter doesn't reject and produces a 0-patch Bezier.
B_SPLINE_SURFACE_WITH_KNOTS degree (3,3), 1 control point, knot multiplicities
(2,2) on both axes.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS u_degree=3, v_degree=3, 1×1 control grid.
    U: n=1 pole, p=3 → n+p+1=5. mults (2,2) sum=4 — this is undersized.
    Note: for n=1 pole, degree=3, knot sum must = 1+3+1=5.
    Use mults (3,2) → sum=5. Or single-span: mults (4,1) sum=5 with knots (0,1).
    Minimal valid STEP form: mults must sum to n+p+1.
    n=1, p=3: sum=5. Use (2,3) or (4,1) -- but only 1 internal knot for 2 values.
    Actually: minimum required n = p+1 = 4 for degree 3. With n=1, invalid.
    Catalog says "knot multiplicities (2,2) on both axes" but that sums to 4
    for n=1, p=3 requiring sum=5. We encode the catalog's intent literally
    (undersized mults) — this is the malformed input that triggers the bug.
    The STEP data is structurally broken by design (n < p+1), which is
    precisely the condition that causes ConvertSurfaceToBezierBasis to produce
    a 0-patch result instead of rejecting.
    IS the face_geometry of the ADVANCED_FACE (mechanism IS the face surface).
  - C-1 DRIVER: 1×1 control grid with degree=3 (n < p+1) causes OCC
    conversion to fail → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS u_degree=3 v_degree=3
    1×1 control grid (n=1, requires n≥4 for degree-3); knots (0.0,1.0)
    mults (2,2) — intentionally undersized; IS face_geometry;
    ConvertSurfaceToBezierBasis produces 0-patch Bezier instead of rejecting.
  - C-1 DRIVER: degenerate 1×1 grid with degree=3 → invalid shape → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn095",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS u_degree=3 v_degree=3 1x1-control-grid; "
        "n=1 but degree=3 requires n≥4; knots (0.0,1.0) mults (2,2) undersized; "
        "IS face_geometry; "
        "ConvertSurfaceToBezierBasis 0-patch result → shape_null=True"
    ),
)

# ── CATALOG MECHANISM: 1×1 control grid, degree (3,3) ────────────────────────
# Intentionally broken: n=1 control point, degree=3 requires n≥4.
# Knot mults (2,2) on both axes per catalog (sum=4, should be n+p+1=5 → invalid).
# This is the degenerate input the fixture is demonstrating.
cp = f.cartesian_point((1.0, 1.0, 0.0))
grid = f"(#{cp.eid})"  # wait: STEP requires row-of-rows even for 1x1

# B_SPLINE_SURFACE_WITH_KNOTS args: name, u_degree, v_degree, control_points_list,
#   surface_form, u_closed, v_closed, self_intersect,
#   u_multiplicities, v_multiplicities, u_knots, v_knots, knot_spec
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn095_1x1',3,3,"
    f"((#{cp.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

# ── Degenerate boundary: all 4 corners collapse to the single control point ──
# Face with a single degenerate vertex — all edges share the one point
p_corner = f.cartesian_point((1.0, 1.0, 0.0))
v_corner  = f.vertex_point(p_corner)

# Build a degenerate edge: start==end, zero-length line
d3 = f.direction((1.0, 0.0, 0.0))
v3 = f.vector(d3, 0.0)
line3d = f.line(p_corner, v3)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

pp_s = f.cartesian_point((0.0, 0.0))
d2   = f.direction((1.0, 0.0))
v2   = f.vector(d2, 0.0)
line2d = f.line(pp_s, v2)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn095_pcdef',(#{line2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn095_pc_ent',#{surf.eid},#{defrep.eid})")
sc = f._emit_raw(
    f"SURFACE_CURVE('gn095_sc',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# Degenerate seam edge: start==end
e_seam = f._emit_raw(
    f"EDGE_CURVE('gn095_seam',#{v_corner.eid},#{v_corner.eid},#{sc.eid},.T.)"
)

# Minimal loop with just the one degenerate edge
loop = f.edge_loop([
    f.oriented_edge(e_seam, True),
])

# Mechanism IS the face surface (surf)
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
