"""Gs075 — Cylindrical Surface Seam-Aware Split.

Catalog claim: CYLINDRICAL_SURFACE with angular trim [π/2, 3π/2] spanning the
seam at U=π. ShapeUpgrade_ClosedFaceDivide.SplitSurface() splits at U=π but
loses the seam metadata (parametric discontinuity marker), so downstream code
cannot reconstruct the original closed cylinder from the split halves.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE (radius=5.0) IS inside GEOMETRIC_CURVE_SET aggregate;
    angular trim spanning seam at U=π ([π/2, 3π/2] ≈ [1.5708, 4.7124]) IS the
    defect; SplitSurface loses seam metadata at the split point IS the failure mode.
  - Byte assertions: contains(b'CYLINDRICAL_SURFACE'),
                     contains(b'gs075').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CYLINDRICAL_SURFACE IS the defective surface inside
    GEOMETRIC_CURVE_SET; seam-spanning trim [π/2, 3π/2] requires seam metadata
    to be preserved through SplitSurface() IS the mechanism; seam metadata lost
    on U-split IS the defect; downstream reconstruction fails.
  - shape_null driver: seam metadata loss causes reconstruction failure; strict
    kernels reject; empty result.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs075",
    defect=(
        "CYLINDRICAL_SURFACE (radius=5.0) IS inside GEOMETRIC_CURVE_SET; "
        "angular trim spanning seam at U=pi ([pi/2, 3pi/2]) IS the defect; "
        "SplitSurface splits at U=pi but loses seam metadata (parametric "
        "discontinuity marker) IS the mechanism failure; shape_null"
    ),
)

# ── CYLINDRICAL_SURFACE: radius=5.0, axis along Z ────────────────────────────
# Byte assertion: contains(b'CYLINDRICAL_SURFACE')
# Byte assertion: contains(b'gs075')
cy_orig = f.cartesian_point((0.0, 0.0, 0.0))
cy_zdir = f.direction((0.0, 0.0, 1.0))
cy_xdir = f.direction((1.0, 0.0, 0.0))
cy_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs075_cy_ax',#{cy_orig.eid},#{cy_zdir.eid},#{cy_xdir.eid})"
)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('gs075_cyl',#{cy_ax.eid},5.0)")

# ── Sample points on the cylinder at key angular positions ────────────────────
# U=π/2 (trim start, x≈0, y=5):  cos(π/2)=0, sin(π/2)=1
# U=π   (seam, x=-5, y=0):        cos(π)=-1,  sin(π)=0
# U=3π/2 (trim end, x≈0, y=-5): cos(3π/2)=0, sin(3π/2)=-1
p_trim_lo = f.cartesian_point((0.0,   5.0,  0.0))   # U=π/2 (trim lower bound)
p_seam    = f.cartesian_point((-5.0,  0.0,  0.0))   # U=π   (seam crossing point)
p_trim_hi = f.cartesian_point((0.0,  -5.0,  0.0))   # U=3π/2 (trim upper bound)
p_mid     = f.cartesian_point((0.0,   0.0,  1.0))   # axial midpoint on cylinder

# ── GEOMETRIC_CURVE_SET: aggregate containing the seam-spanning cylinder ──────
# shape_null driver: GEOMETRIC_CURVE_SET with seam-split cylinder yields no BRep
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('gs075_gcs',"
    f"(#{cyl.eid},#{p_trim_lo.eid},#{p_seam.eid},#{p_trim_hi.eid},#{p_mid.eid}))"
)

# ── Minimal product chain so precheck passes ──────────────────────────────────
f.add_product_chain(gcs)
