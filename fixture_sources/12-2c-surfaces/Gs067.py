"""Gs067 — ShapeUpgrade_ConvertSurfaceToBezierBasis: OFFSET_SURFACE with negative distance.

Catalog claim: OFFSET_SURFACE wrapping PLANE with a negative distance (-2.5mm)
ought to produce a plane on the opposite side of the base plane. The converter
may collapse the offset if not handling sign-flipped surfaces correctly,
producing an untrimmed or inverted Bezier that degenerates rather than
maintaining the parallel-plane property with opposite normal.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - OFFSET_SURFACE (distance=-2.5) wrapping PLANE IS inside GEOMETRIC_CURVE_SET
    aggregate; negative distance IS the sign-flip defect; ConvertSurfaceToBezierBasis
    ignores sign, collapses the offset IS the failure mode.
  - Byte assertions: contains(b'OFFSET_SURFACE'),
                     contains(b'-2.5').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: OFFSET_SURFACE (negative_offset_value=-2.5) wrapping PLANE
    IS the defective surface inside GEOMETRIC_CURVE_SET; negative distance flips the
    normal direction IS the semantics; ConvertSurfaceToBezierBasis ignores sign and
    collapses the offset IS the defect.
  - shape_null driver: Bezier conversion degenerates negative-offset surface;
    strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs067",
    defect=(
        "OFFSET_SURFACE (distance=-2.5) wrapping PLANE IS inside GEOMETRIC_CURVE_SET; "
        "negative distance (sign-flipped offset, plane on opposite side) IS the defect; "
        "ConvertSurfaceToBezierBasis ignores offset sign, collapses or inverts surface "
        "IS the mechanism failure; shape_null"
    ),
)

# ── Base PLANE: XY-plane through origin, Z-normal ────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs067_pl_ax',#{pl_orig.eid},#{pl_zdir.eid},#{pl_xdir.eid})"
)
plane = f._emit_raw(f"PLANE('gs067_plane',#{pl_ax.eid})")

# ── OFFSET_SURFACE: negative distance -2.5 (plane at z=+2.5 via inverted normal) ──
# Byte assertion: contains(b'OFFSET_SURFACE')
# Byte assertion: contains(b'-2.5')
# OFFSET_SURFACE(name, basis_surface, distance, self_intersect)
# distance=-2.5 means offset in the -Z direction from XY-plane → z=-2.5
offset_surf = f._emit_raw(
    f"OFFSET_SURFACE('gs067_offset',#{plane.eid},-2.5,.F.)"
)

# ── Sample points bracketing the offset plane location ────────────────────────
# Base plane at z=0; negative offset target at z=-2.5; opposite side at z=+2.5
p_base    = f.cartesian_point((0.0,  0.0,  0.0))   # on base PLANE
p_offset  = f.cartesian_point((0.0,  0.0, -2.5))   # expected offset plane location
p_corner  = f.cartesian_point((1.0,  1.0, -2.5))   # corner at offset z

# ── GEOMETRIC_CURVE_SET: aggregate containing the negative-offset surface ─────
# shape_null driver: GEOMETRIC_CURVE_SET with collapsed negative-offset yields no BRep
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('gs067_gcs',"
    f"(#{offset_surf.eid},#{p_base.eid},#{p_offset.eid},#{p_corner.eid}))"
)

# ── Minimal product chain so precheck passes ──────────────────────────────────
f.add_product_chain(gcs)
