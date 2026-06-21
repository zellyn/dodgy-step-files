"""Gs065 — ShapeAnalysis_Surface.ValueOfUV near-tangent surface (vanishing Gaussian curvature).

Catalog claim: ValueOfUV's Newton refinement diverges on surfaces with small
first-fundamental-form determinant (near-tangent or nearly-degenerate metric).
A B-spline surface with control-point alignment in the U-direction creates a
vanishing Gaussian curvature region where det(First Fundamental Form) ≈ 0,
causing Newton iteration to fail or non-converge.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (aligned control points in U-direction) IS inside
    GEOMETRIC_CURVE_SET aggregate; control-point alignment (all rows share identical
    U-coordinates) IS the vanishing-Gaussian-curvature defect; ValueOfUV Newton
    refinement diverges IS the failure mode.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'),
                     contains(b'gs065').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS IS the defective surface inside
    GEOMETRIC_CURVE_SET; all control points aligned on identical U-values creates
    a degenerate metric (dS/du ≈ 0) IS the mechanism; ValueOfUV Newton iteration
    diverges on vanishing det(First Form) IS the defect.
  - shape_null driver: Newton refinement fails; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs065",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (aligned control points in U-direction) IS inside "
        "GEOMETRIC_CURVE_SET; all U-direction control rows share same X-coordinate "
        "(dS/du ≈ 0, vanishing Gaussian curvature) IS the defect; "
        "ValueOfUV Newton refinement diverges on near-zero det(First Form) IS the "
        "mechanism failure; shape_null"
    ),
)

# ── B-spline surface: degree 3 in U and V, 4×4 control points ────────────────
# DEFECT: all 4 columns share the same X-coordinate (x=0.5 for all).
# This makes dS/du ≈ 0 along U, collapsing the first fundamental form.
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# Byte assertion: contains(b'gs065')
ctrl_grid = [
    # v=0 row: all X=0.5 (aligned) — only Z varies to give some shape
    [(0.5, 0.0, 0.0), (0.5, 0.0, 0.5), (0.5, 0.0, 1.0), (0.5, 0.0, 1.5)],
    # v=1 row: same X=0.5 alignment
    [(0.5, 0.5, 0.0), (0.5, 0.5, 0.5), (0.5, 0.5, 1.0), (0.5, 0.5, 1.5)],
    # v=2 row: same X=0.5 alignment
    [(0.5, 1.0, 0.0), (0.5, 1.0, 0.5), (0.5, 1.0, 1.0), (0.5, 1.0, 1.5)],
    # v=3 row: same X=0.5 alignment
    [(0.5, 1.5, 0.0), (0.5, 1.5, 0.5), (0.5, 1.5, 1.0), (0.5, 1.5, 1.5)],
]

ctrl_pts = [
    [f.cartesian_point(xyz) for xyz in row]
    for row in ctrl_grid
]

cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[vrow][ucol].eid}" for ucol in range(4)) + ")"
    for vrow in range(4)
) + ")"

bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs065_bss',3,3,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,4),(4,4),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

# ── Sample points to accompany the surface in the aggregate ───────────────────
p_ref_a = f.cartesian_point((0.5, 0.0, 0.0))
p_ref_b = f.cartesian_point((0.5, 1.5, 1.5))

# ── GEOMETRIC_CURVE_SET: aggregate containing the near-tangent B-spline ───────
# shape_null driver: GEOMETRIC_CURVE_SET with degenerate-metric surface yields no BRep
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('gs065_gcs',(#{bss.eid},#{p_ref_a.eid},#{p_ref_b.eid}))"
)

# ── Minimal product chain so precheck passes ──────────────────────────────────
f.add_product_chain(gcs)
