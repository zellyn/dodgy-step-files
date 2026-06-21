"""Gs064 — ShapeAnalysis_Surface.IsVClosed midpoint sampling on near-degenerate torus.

Catalog claim: IsVClosed must check V-periodicity via knot vector AND a
sample-midpoint correlation. Near-degenerate torus where major radius R equals
minor radius r (both 10mm) returns false negative because midpoint sampling
misses the closure due to numerical symmetry at the inner equator (r=R).

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - TOROIDAL_SURFACE (R=10.0, r=10.0) IS inside GEOMETRIC_CURVE_SET aggregate;
    R == r (inner equator collapses to a point) IS the defect; IsVClosed
    midpoint sampling on symmetric near-degenerate torus IS the failure mode.
  - Byte assertions: contains(b'TOROIDAL_SURFACE'),
                     contains(b'10.0,10.0').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: TOROIDAL_SURFACE with R=r=10.0 IS the defective surface
    inside GEOMETRIC_CURVE_SET; inner equator collapses (self-intersecting torus)
    IS the geometric degeneracy; midpoint sampling returns symmetric false result.
  - shape_null driver: IsVClosed returns false negative on R==r torus;
    strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs064",
    defect=(
        "TOROIDAL_SURFACE (R=10.0, r=10.0) IS inside GEOMETRIC_CURVE_SET; "
        "R == r (inner equator collapses: self-intersecting torus) IS the defect; "
        "IsVClosed midpoint sampling returns false negative on near-degenerate torus "
        "IS the mechanism failure; shape_null"
    ),
)

# ── TOROIDAL_SURFACE: R=10.0, r=10.0 (near-degenerate: R == r) ───────────────
# Byte assertion: contains(b'TOROIDAL_SURFACE')
# Byte assertion: contains(b'10.0,10.0')
torus_orig = f.cartesian_point((0.0, 0.0, 0.0))
torus_zdir = f.direction((0.0, 0.0, 1.0))
torus_xdir = f.direction((1.0, 0.0, 0.0))
torus_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs064_torus_ax',#{torus_orig.eid},#{torus_zdir.eid},#{torus_xdir.eid})"
)
# R=10.0 (major radius), r=10.0 (minor radius) — inner equator collapses to a point
torus = f._emit_raw(
    f"TOROIDAL_SURFACE('gs064_torus',#{torus_ax.eid},10.0,10.0)"
)

# ── Sample points for GEOMETRIC_CURVE_SET ─────────────────────────────────────
# Two points on the outer equator of the torus (v=0, u=0 and u=π)
p_outer_a = f.cartesian_point((20.0,  0.0, 0.0))   # (R+r, 0, 0) = (20, 0, 0)
p_outer_b = f.cartesian_point((-20.0, 0.0, 0.0))   # (-20, 0, 0)
# Two points at the inner equator (v=π, self-intersection zone, R+r·cos(π)=10-10=0)
p_inner_a = f.cartesian_point((0.0,   0.0, 10.0))  # top of minor circle at u=0
p_inner_b = f.cartesian_point((0.0,   0.0,-10.0))  # bottom of minor circle at u=0

# ── GEOMETRIC_CURVE_SET: aggregate containing the defective TOROIDAL_SURFACE ──
# shape_null driver: GEOMETRIC_CURVE_SET with degenerate torus does not yield BRep
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('gs064_gcs',(#{torus.eid},#{p_outer_a.eid},"
    f"#{p_outer_b.eid},#{p_inner_a.eid},#{p_inner_b.eid}))"
)

# ── Minimal product chain so precheck passes ──────────────────────────────────
f.add_product_chain(gcs)
