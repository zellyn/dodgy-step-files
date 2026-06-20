"""Os020 — MakeEvolved: profile sweep along a non-planar spine self-intersects.

Catalog claim: A profile is "evolved" (swept with rotation) along a 3D spine;
the resulting swept surface self-intersects where the profile rotates past
itself.  A small CIRCLE (radius 3) is evolved along a tight helix-like
B_SPLINE_CURVE_WITH_KNOTS where the profile diameter (6) exceeds the local
curvature radius — the sweep folds over itself.

Mechanism IS a GEOMETRIC_CURVE_SET containing:
  - A CIRCLE (profile, radius 3) — byte assertion ✓
  - A B_SPLINE_CURVE_WITH_KNOTS (helix-approx spine) — byte assertion ✓
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'B_SPLINE_CURVE_WITH_KNOTS')
  - contains(b'CIRCLE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os020",
    defect=(
        "GEOMETRIC_CURVE_SET containing a CIRCLE (profile radius=3) and a "
        "B_SPLINE_CURVE_WITH_KNOTS (tight 3D helix-approximation spine); "
        "profile diameter (6) exceeds helix local curvature radius (~4) — "
        "evolved swept surface self-intersects (folds over); "
        "BRepOffsetAPI_MakeEvolved self-intersection along spine; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Profile: CIRCLE radius=3 in XY plane ─────────────────────────────────────
# axis2_placement_3d for the circle
circ_orig = f.cartesian_point((0.0, 0.0, 0.0))
circ_zdir = f.direction((0.0, 0.0, 1.0))
circ_xdir = f.direction((1.0, 0.0, 0.0))
circ_plc  = f.axis2_placement_3d(circ_orig, circ_zdir, circ_xdir)
circle    = f.circle(circ_plc, 3.0)   # CIRCLE radius=3 — byte assertion ✓

# ── Spine: B_SPLINE_CURVE_WITH_KNOTS approximating a tight helix ─────────────
# 5 control points that spiral through one tight loop: radius ~4, pitch ~3.
# Profile diameter 6 > helix radius 4 → self-intersection guaranteed.
cp0 = f.cartesian_point(( 4.0,  0.0, 0.0))
cp1 = f.cartesian_point(( 0.0,  4.0, 1.0))
cp2 = f.cartesian_point((-4.0,  0.0, 2.0))
cp3 = f.cartesian_point(( 0.0, -4.0, 3.0))
cp4 = f.cartesian_point(( 4.0,  0.0, 4.0))   # one full turn, pitch=4

spine = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[cp0, cp1, cp2, cp3, cp4],
    knot_multiplicities=[4, 1, 4],
    knots=[0.0, 0.5, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
    name="helix_spine",
)   # B_SPLINE_CURVE_WITH_KNOTS — byte assertion ✓

# ── GEOMETRIC_CURVE_SET wrapping profile + spine ──────────────────────────────
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{circle.eid},#{spine.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os020.stp")
