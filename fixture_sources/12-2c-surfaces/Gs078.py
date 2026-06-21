"""Gs078 — Offset-of-Offset Sign Error.

Catalog claim: OFFSET_SURFACE wrapping OFFSET_SURFACE wrapping PLANE — nested
offset accumulation has a sign error in ShapeUpgrade_ConvertSurfaceToBezierBasis.
Each offset is +0.5, so the accumulated result should be Z=+1.0, but the
conversion computes Z=0.0 or Z=-1.0 due to a sign flip in the recursive chain.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - OFFSET_SURFACE (distance=+0.5) wrapping OFFSET_SURFACE (distance=+0.5)
    wrapping PLANE IS inside GEOMETRIC_CURVE_SET aggregate; nested offset chain
    (total expected offset = +1.0) IS the defect; ConvertSurfaceToBezierBasis
    sign error in recursive offset produces Z=0 or Z=-1 IS the failure mode.
  - Byte assertions: contains(b'OFFSET_SURFACE'),
                     contains(b'gs078').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: nested OFFSET_SURFACE (outer wraps inner wraps PLANE) IS
    the defective entity inside GEOMETRIC_CURVE_SET; sign accumulation across two
    +0.5 offsets should yield +1.0 IS the expected behavior; recursive Bezier
    conversion negates one sign IS the defect; Z-coordinate at origin becomes 0
    or -1 instead of +1.
  - shape_null driver: incorrect nested offset produces degenerate or inverted
    Bezier; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs078",
    defect=(
        "nested OFFSET_SURFACE (outer +0.5 wraps inner +0.5 wrapping PLANE) IS inside "
        "GEOMETRIC_CURVE_SET; total expected Z-offset = +1.0 IS the correct result; "
        "ConvertSurfaceToBezierBasis sign error in recursive offset chain IS the "
        "mechanism failure; computes Z=0.0 or Z=-1.0 instead of +1.0; shape_null"
    ),
)

# ── Base PLANE: XY-plane through origin, Z-normal ─────────────────────────────
# Byte assertion: contains(b'OFFSET_SURFACE')
# Byte assertion: contains(b'gs078')
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs078_pl_ax',#{pl_orig.eid},#{pl_zdir.eid},#{pl_xdir.eid})"
)
plane = f._emit_raw(f"PLANE('gs078_base_plane',#{pl_ax.eid})")

# ── Inner OFFSET_SURFACE: +0.5 above XY-plane → expected Z=+0.5 ───────────────
# OFFSET_SURFACE(name, basis_surface, distance, self_intersect)
inner_offset = f._emit_raw(
    f"OFFSET_SURFACE('gs078_inner_offset',#{plane.eid},0.5,.F.)"
)

# ── Outer OFFSET_SURFACE: +0.5 above inner offset → expected Z=+1.0 ──────────
# Recursive chain: PLANE (Z=0) → +0.5 → +0.5 = Z=+1.0
# ConvertSurfaceToBezierBasis sign error: may produce Z=0 or Z=-1.0
outer_offset = f._emit_raw(
    f"OFFSET_SURFACE('gs078_outer_offset',#{inner_offset.eid},0.5,.F.)"
)

# ── Sample points at expected and actual (buggy) Z positions ──────────────────
p_base     = f.cartesian_point((0.0, 0.0,  0.0))   # base PLANE at Z=0
p_inner_z  = f.cartesian_point((0.0, 0.0,  0.5))   # inner offset target (Z=+0.5)
p_expected = f.cartesian_point((0.0, 0.0,  1.0))   # expected final Z=+1.0
p_buggy    = f.cartesian_point((0.0, 0.0, -1.0))   # buggy sign-flipped Z=-1.0

# ── GEOMETRIC_CURVE_SET: aggregate containing the nested offset chain ──────────
# shape_null driver: GEOMETRIC_CURVE_SET with sign-errored nested offset yields no BRep
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('gs078_gcs',"
    f"(#{outer_offset.eid},#{inner_offset.eid},"
    f"#{p_base.eid},#{p_inner_z.eid},#{p_expected.eid},#{p_buggy.eid}))"
)

# ── Minimal product chain so precheck passes ──────────────────────────────────
f.add_product_chain(gcs)
