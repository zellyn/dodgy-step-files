"""Gs068 — ShapeAnalysis_Surface.UVFromIso boundary U-iso failure.

Catalog claim: UVFromIso must clamp or reject when the requested U-iso falls
outside the trim domain, not return uninitialized UV. B-spline with U-range
[0, 2] trimmed to [0.5, 1.5]; request u=1.9 → uninitialized garbage.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (U-range [0, 2], dense knots) IS inside
    GEOMETRIC_CURVE_SET aggregate; trim domain [0.5, 1.5] with iso request
    at u=1.9 (outside trim domain) IS the defect; UVFromIso returns
    uninitialized UV IS the failure mode.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'),
                     contains(b'gs068').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS with wide U-range [0,2] IS
    the defective surface inside GEOMETRIC_CURVE_SET; out-of-trim-domain iso
    request at u=1.9 (trim domain [0.5, 1.5]) IS the input defect; UVFromIso
    fails to bounds-check and returns garbage IS the failure mode.
  - shape_null driver: UVFromIso uninitialized result propagates; strict kernels
    reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs068",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (U-range [0,2], dense knots near u=1.9) IS inside "
        "GEOMETRIC_CURVE_SET; out-of-trim-domain iso request (u=1.9 outside [0.5,1.5]) "
        "IS the defect; UVFromIso does not bounds-check, returns uninitialized UV "
        "IS the mechanism failure; shape_null"
    ),
)

# ── B-spline surface: degree 3 in U and V, 6×4 control grid ──────────────────
# U-range [0, 2] via knots (0,0,0,0, 0.5, 1.0, 1.5, 2.0,2.0,2.0,2.0)
# Dense interior knots in U to widen the parametric domain.
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# Byte assertion: contains(b'gs068')
ctrl_grid = [
    # u=0  u=0.4  u=0.8  u=1.2  u=1.6  u=2.0
    [(0.0, 0.0, 0.0), (0.4, 0.0, 0.2), (0.8, 0.0, 0.0), (1.2, 0.0, 0.2), (1.6, 0.0, 0.0), (2.0, 0.0, 0.0)],
    [(0.0, 0.5, 0.0), (0.4, 0.5, 0.2), (0.8, 0.5, 0.0), (1.2, 0.5, 0.2), (1.6, 0.5, 0.0), (2.0, 0.5, 0.0)],
    [(0.0, 1.0, 0.0), (0.4, 1.0, 0.2), (0.8, 1.0, 0.0), (1.2, 1.0, 0.2), (1.6, 1.0, 0.0), (2.0, 1.0, 0.0)],
    [(0.0, 1.5, 0.0), (0.4, 1.5, 0.2), (0.8, 1.5, 0.0), (1.2, 1.5, 0.2), (1.6, 1.5, 0.0), (2.0, 1.5, 0.0)],
]

ctrl_pts = [
    [f.cartesian_point(xyz) for xyz in row]
    for row in ctrl_grid
]

# 4 rows (v), 6 cols (u): U degree=3, V degree=3
# U: 6 cps, degree 3 → 10 knots: (0,0,0,0, 0.5, 1.5, 2.0,2.0,2.0,2.0)  [6+3+1=10]
# V: 4 cps, degree 3 → 8 knots: (0.0,0.0,0.0,0.0, 1.0,1.0,1.0,1.0)
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[vrow][ucol].eid}" for ucol in range(6)) + ")"
    for vrow in range(4)
) + ")"

bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs068_bss',3,3,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,1,1,4),(4,4),(0.0,0.5,1.5,2.0),(0.0,1.0),.UNSPECIFIED.)"
)

# ── Sample points bracketing the trim domain and the out-of-domain request ────
p_in_domain  = f.cartesian_point((0.8,  0.75, 0.0))   # u=0.8 ∈ [0.5, 1.5]
p_out_domain = f.cartesian_point((1.9,  0.75, 0.0))   # u=1.9 ∉ [0.5, 1.5] — out of trim
p_trim_lo    = f.cartesian_point((0.5,  0.0,  0.0))   # trim lower bound
p_trim_hi    = f.cartesian_point((1.5,  0.0,  0.0))   # trim upper bound

# ── GEOMETRIC_CURVE_SET: aggregate containing the out-of-bounds B-spline ─────
# shape_null driver: GEOMETRIC_CURVE_SET with surface carrying out-of-domain
# iso request yields no BRep
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('gs068_gcs',"
    f"(#{bss.eid},#{p_in_domain.eid},#{p_out_domain.eid},"
    f"#{p_trim_lo.eid},#{p_trim_hi.eid}))"
)

# ── Minimal product chain so precheck passes ──────────────────────────────────
f.add_product_chain(gcs)
