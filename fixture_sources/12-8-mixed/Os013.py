"""Os013 — Pipe section plane does not intersect the guide curve.

Catalog claim: A pipe / sweep operation places the section profile on a plane
that, evaluated along the guide curve, never intersects the guide.
Guide curve is a LINE along the X axis at z=0.  Section plane at z=10, normal
(0,0,1).  The plane is parallel to the guide at non-zero offset, so they never
intersect.

Mechanism IS a GEOMETRIC_CURVE_SET containing:
  - A PLANE at z=10 with normal (0,0,1) — the section plane
  - A LINE along the X axis at z=0 — the guide curve
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'PLANE')
  - contains(b'LINE')
  - contains(b'10.0')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os013",
    defect=(
        "GEOMETRIC_CURVE_SET containing a PLANE (section plane at z=10.0) and "
        "a LINE (guide curve along X axis at z=0); "
        "PLANE normal (0,0,1) is parallel to the LINE direction — they never "
        "intersect; pipe sweep PlaneNotIntersectGuide; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Guide: LINE along X axis at z=0 ──────────────────────────────────────────
guide_pt  = f.cartesian_point((0.0, 0.0, 0.0))
guide_dir = f.direction((1.0, 0.0, 0.0))
guide_vec = f.vector(guide_dir, 20.0)
guide_ln  = f.line(guide_pt, guide_vec)   # LINE — byte assertion ✓

# ── Section plane at z=10, normal (0,0,1) ────────────────────────────────────
# AXIS2_PLACEMENT_3D: location=(0,0,10), axis=(0,0,1), ref_dir=(1,0,0)
pl_orig = f.cartesian_point((0.0, 0.0, 10.0))   # z=10.0 — byte assertion ✓
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)                        # PLANE — byte assertion ✓

# ── GEOMETRIC_CURVE_SET wrapping guide + section plane ───────────────────────
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{guide_ln.eid},#{plane.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os013.stp")
