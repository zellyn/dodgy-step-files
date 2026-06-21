"""Gs076 — Newton Fallback Comparison Bias.

Catalog claim: ShapeAnalysis_Surface.NextValueOfUV — Newton iteration fails to
converge on saddle surface; the fallback multi-root comparison uses absolute
distance in 3D space rather than normalized parameter distance, causing the wrong
root to be selected ((1.8, 0.9) instead of the expected (0.2, 0.1)).

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (saddle shape: mixed curvature in U and V) IS
    inside GEOMETRIC_CURVE_SET aggregate; inflection zone near (0.3, 0.7) where
    Newton fails and fallback picks wrong root IS the defect; unnormalized
    parameter comparison selects (1.8, 0.9) instead of (0.2, 0.1).
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'),
                     contains(b'gs076').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (saddle: Z = X² - Y²) IS the
    defective surface inside GEOMETRIC_CURVE_SET; multi-root ambiguity near
    inflection IS the numerical context; fallback uses absolute vs normalized
    parameter distance IS the algorithm defect; wrong root selected.
  - shape_null driver: wrong-root selection produces off-surface projection;
    strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs076",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (saddle surface: mixed curvature in U and V) "
        "IS inside GEOMETRIC_CURVE_SET; Newton fails near inflection at (0.3, 0.7); "
        "fallback multi-root comparison uses absolute 3D distance not normalized "
        "parameter distance IS the mechanism failure; selects wrong root; shape_null"
    ),
)

# ── Saddle B-spline surface: Z = X² - Y² (hyperbolic paraboloid) ─────────────
# Degree 2 in both U and V, 3×3 control points spanning [0,2]×[0,2] in param space.
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# Byte assertion: contains(b'gs076')
#
# Control points arranged so the surface has saddle shape (Z positive in X-diag,
# negative in Y-diag):
#   At (u=0,v=0): (0, 0, +1)   At (u=1,v=0): (1, 0, 0)    At (u=2,v=0): (2, 0, +1)
#   At (u=0,v=1): (0, 1,  0)   At (u=1,v=1): (1, 1, 0)    At (u=2,v=1): (2, 1,  0)
#   At (u=0,v=2): (0, 2, -1)   At (u=1,v=2): (1, 2, 0)    At (u=2,v=2): (2, 2, -1)
ctrl_grid = [
    # v=0 row
    [(0.0, 0.0,  1.0), (1.0, 0.0,  0.0), (2.0, 0.0,  1.0)],
    # v=1 row (saddle midplane)
    [(0.0, 1.0,  0.0), (1.0, 1.0,  0.0), (2.0, 1.0,  0.0)],
    # v=2 row
    [(0.0, 2.0, -1.0), (1.0, 2.0,  0.0), (2.0, 2.0, -1.0)],
]

ctrl_pts = [
    [f.cartesian_point(xyz) for xyz in row]
    for row in ctrl_grid
]

# 3×3 grid, degree 2 in both U and V
# Knots: U=(0.0,0.0,0.0, 2.0,2.0,2.0), V=(0.0,0.0,0.0, 2.0,2.0,2.0)
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[vrow][ucol].eid}" for ucol in range(3)) + ")"
    for vrow in range(3)
) + ")"

bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs076_saddle',2,2,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3),(3,3),(0.0,2.0),(0.0,2.0),.UNSPECIFIED.)"
)

# ── Sample points marking the multi-root ambiguity zone ───────────────────────
p_query   = f.cartesian_point((0.3, 0.7,  0.0))   # query point near inflection
p_root_a  = f.cartesian_point((0.2, 0.1,  0.0))   # correct root (near query param)
p_root_b  = f.cartesian_point((1.8, 0.9,  0.0))   # wrong root selected by fallback

# ── GEOMETRIC_CURVE_SET: aggregate containing the saddle surface ───────────────
# shape_null driver: GEOMETRIC_CURVE_SET with saddle-surface wrong-root projection
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('gs076_gcs',"
    f"(#{bss.eid},#{p_query.eid},#{p_root_a.eid},#{p_root_b.eid}))"
)

# ── Minimal product chain so precheck passes ──────────────────────────────────
f.add_product_chain(gcs)
