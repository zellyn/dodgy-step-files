"""Gs074 — Plane Singularity Misclassification.

Catalog claim: ShapeAnalysis_Surface::Singularity() reports false positives for
planar geometry when called with a large rectangular trim domain [-100,100]×[-100,100].
Planes have no singularities by definition; the algorithm should reject planes
early but instead reports a spurious singularity location.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - PLANE (XY-plane through origin) IS inside GEOMETRIC_CURVE_SET aggregate;
    large rectangular trim domain [-100,100]×[-100,100] creates the numerical
    context IS the defect; Singularity() falsely reports singularity on plane
    IS the failure mode.
  - Byte assertions: contains(b'PLANE'),
                     contains(b'gs074').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE IS the defective surface inside GEOMETRIC_CURVE_SET;
    large trim domain [-100,100]×[-100,100] (planes extend to infinity) IS the
    numerical context; Singularity() fails to reject plane early and reports
    false positive IS the defect.
  - shape_null driver: false singularity classification causes strict kernels to
    reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs074",
    defect=(
        "PLANE (XY-plane, origin) IS inside GEOMETRIC_CURVE_SET; large rectangular "
        "trim domain [-100,100]x[-100,100] IS the numerical context; "
        "Singularity() reports false positive singularity on plane (planes have none "
        "by definition) IS the mechanism failure; shape_null"
    ),
)

# ── PLANE: standard XY-plane through origin ───────────────────────────────────
# Byte assertion: contains(b'PLANE')
# Byte assertion: contains(b'gs074')
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs074_pl_ax',#{pl_orig.eid},#{pl_zdir.eid},#{pl_xdir.eid})"
)
plane = f._emit_raw(f"PLANE('gs074_plane',#{pl_ax.eid})")

# ── Sample points at the large trim domain corners [-100,100]×[-100,100] ──────
# These represent the large parametric domain extent that confuses Singularity()
p_sw  = f.cartesian_point((-100.0, -100.0, 0.0))   # SW corner of trim domain
p_ne  = f.cartesian_point(( 100.0,  100.0, 0.0))   # NE corner of trim domain
p_nw  = f.cartesian_point((-100.0,  100.0, 0.0))   # NW corner
p_se  = f.cartesian_point(( 100.0, -100.0, 0.0))   # SE corner
p_ctr = f.cartesian_point((   0.0,    0.0, 0.0))   # plane origin (no singularity here)

# ── GEOMETRIC_CURVE_SET: aggregate containing the plane + trim corners ────────
# shape_null driver: GEOMETRIC_CURVE_SET with plane reported as singular yields no BRep
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('gs074_gcs',"
    f"(#{plane.eid},#{p_sw.eid},#{p_ne.eid},#{p_nw.eid},#{p_se.eid},#{p_ctr.eid}))"
)

# ── Minimal product chain so precheck passes ──────────────────────────────────
f.add_product_chain(gcs)
