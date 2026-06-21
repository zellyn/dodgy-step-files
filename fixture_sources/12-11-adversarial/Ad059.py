"""Ad059 — Mismatched weight / pole counts in B-spline (writer-emitted OOB-read).

Catalog claim: RATIONAL_BSPLINE_CURVE with weights array length != poles
array length; reader walks past end of weights vector. STEP writer bug
(Mantis 0030921) emits mismatched arrays; downstream reader OOB-reads.

Reproducer recipe: RATIONAL_B_SPLINE_CURVE with weights (1.,1.,1.) — 3
entries — and poles (#1,#2,#3,#4) — 4 entries — so weights array is one
element shorter than poles.

Byte assertions:
  contains(b'RATIONAL_B_SPLINE_CURVE') or matches(rb'RATIONAL_BSPLINE_CURVE[(][(][^)]+[)][)]')
  contains(b'B_SPLINE_CURVE_WITH_KNOTS') or contains(b'BSPLINE') or contains(b'RATIONAL_B_SPLINE_CURVE')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad059",
    defect=(
        "mismatched weight/pole count in RATIONAL_B_SPLINE_CURVE: "
        "weights (1.,1.,1.) has 3 entries but poles list has 4 entries; "
        "reader walks past end of weights vector → OOB-read; "
        "writer-emitted bug: Mantis 0030921 (G024); "
        "See also Gn002; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload: B_SPLINE_CURVE_WITH_KNOTS + RATIONAL_B_SPLINE_CURVE
# using a complex entity instance.
#
# We need 4 control points (poles) and only 3 weights — the mismatch is
# the defect.  The combined complex instance form used by AP214 writers is:
#
#   (B_SPLINE_CURVE_WITH_KNOTS(...) RATIONAL_B_SPLINE_CURVE(...))
#
# We emit the B_SPLINE_CURVE_WITH_KNOTS base first, then a combined entity.

# 4 control-point poles.
p0 = f._emit_raw("CARTESIAN_POINT('p0',(0.,0.,0.))")
p1 = f._emit_raw("CARTESIAN_POINT('p1',(1.,1.,0.))")
p2 = f._emit_raw("CARTESIAN_POINT('p2',(2.,0.,0.))")
p3 = f._emit_raw("CARTESIAN_POINT('p3',(3.,1.,0.))")

# Complex instance: B_SPLINE_CURVE_WITH_KNOTS combined with
# RATIONAL_B_SPLINE_CURVE.
# B_SPLINE_CURVE_WITH_KNOTS args:
#   name, degree, control_points_list, curve_form, closed_curve, self_intersect,
#   knot_multiplicities, knots, knot_spec
# RATIONAL_B_SPLINE_CURVE args:
#   weights_data  ← only 3 entries vs 4 poles → the defect
#
# Satisfies: contains(b'B_SPLINE_CURVE_WITH_KNOTS')
#            contains(b'RATIONAL_B_SPLINE_CURVE')
f._emit_raw(
    f"(B_SPLINE_CURVE_WITH_KNOTS('mismatch',3,"
    f"(#{p0.eid},#{p1.eid},#{p2.eid},#{p3.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,4),(0.,1.),.PIECEWISE_BEZIER_KNOTS.)"
    f"RATIONAL_B_SPLINE_CURVE((1.,1.,1.)))"
)

# Second standalone RATIONAL_B_SPLINE_CURVE entity to reinforce the byte
# assertion (contains(b'RATIONAL_B_SPLINE_CURVE')).
f._emit_raw(
    f"RATIONAL_B_SPLINE_CURVE((1.,1.,1.))"
)
