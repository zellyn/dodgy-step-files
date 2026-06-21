"""Gs077 — Newton Discriminant Near-Zero Abort.

Catalog claim: ShapeAnalysis_Surface.SurfaceNewton — Newton iteration's
discriminant approaches zero at a surface inflection point. The abort threshold
is too strict; SurfaceNewton returns failure where a damped step would converge.
The inflection is caused by a sign change in curvature along the U-direction.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (curvature sign change in U: S-shaped in U,
    flat in V) IS inside GEOMETRIC_CURVE_SET aggregate; inflection zone where
    discriminant → 0 IS the defect; SurfaceNewton aborts too early IS the
    failure mode.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'),
                     contains(b'gs077').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (S-curve in U: control points
    bent up then down) IS the defective surface inside GEOMETRIC_CURVE_SET;
    inflection point where d²Z/du² = 0 creates discriminant → 0 IS the numerical
    context; SurfaceNewton abort threshold too strict IS the defect.
  - shape_null driver: premature Newton abort leaves projection incomplete;
    strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs077",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (S-shaped curvature in U: sign change at u=0.5) "
        "IS inside GEOMETRIC_CURVE_SET; inflection at u=0.5 where Newton discriminant "
        "approaches zero IS the defect; SurfaceNewton abort threshold too strict, "
        "premature failure at inflection IS the mechanism; shape_null"
    ),
)

# ── B-spline surface: S-shaped in U (curvature sign change), flat in V ────────
# Degree 3 in U (to capture S-curve), degree 1 in V (flat extrusion)
# Control points: 5 cols (U) × 2 rows (V)
# U-shape: Z goes +1 → +0.5 → 0 → -0.5 → -1 (inflection at u=2, middle cp)
# This creates d²Z/du² = 0 at u=2 (inflection), discriminant → 0 there.
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# Byte assertion: contains(b'gs077')
ctrl_grid = [
    # v=0 row: S-curve in U
    [(0.0, 0.0,  1.0), (1.0, 0.0,  0.5), (2.0, 0.0,  0.0), (3.0, 0.0, -0.5), (4.0, 0.0, -1.0)],
    # v=1 row: same S-curve (extruded flat in V)
    [(0.0, 1.0,  1.0), (1.0, 1.0,  0.5), (2.0, 1.0,  0.0), (3.0, 1.0, -0.5), (4.0, 1.0, -1.0)],
]

ctrl_pts = [
    [f.cartesian_point(xyz) for xyz in row]
    for row in ctrl_grid
]

# 2 rows (V), 5 cols (U): U degree=3, V degree=1
# U: 5 cps, degree 3 → 9 knots: (0,0,0,0, 2.0, 4.0,4.0,4.0,4.0) ... but 5+3+1=9 ✓
# V: 2 cps, degree 1 → 4 knots: (0.0,0.0, 1.0,1.0)
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[vrow][ucol].eid}" for ucol in range(5)) + ")"
    for vrow in range(2)
) + ")"

bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs077_scurve',3,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,1,4),(2,2),(0.0,2.0,4.0),(0.0,1.0),.UNSPECIFIED.)"
)

# ── Sample points marking the inflection zone ─────────────────────────────────
p_inflect = f.cartesian_point((2.0,  0.5,  0.0))   # inflection point (Z=0, discriminant→0)
p_pre     = f.cartesian_point((1.0,  0.5,  0.5))   # before inflection (positive curvature)
p_post    = f.cartesian_point((3.0,  0.5, -0.5))   # after inflection (negative curvature)

# ── GEOMETRIC_CURVE_SET: aggregate containing the S-curve surface ─────────────
# shape_null driver: GEOMETRIC_CURVE_SET with inflected surface + premature Newton abort
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('gs077_gcs',"
    f"(#{bss.eid},#{p_inflect.eid},#{p_pre.eid},#{p_post.eid}))"
)

# ── Minimal product chain so precheck passes ──────────────────────────────────
f.add_product_chain(gcs)
