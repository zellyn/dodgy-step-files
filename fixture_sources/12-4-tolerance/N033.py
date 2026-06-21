"""N033 — Tolerance value polymorphic encoding (MeasureRepresentationItem vs plain measure).

STEP_SHAPE_TOLERANCE_VALUE bounds may be encoded via plain
LENGTH_MEASURE_WITH_UNIT, via StepRepr_ReprItemAndMeasureWithUnit, or via
AP242 complex form. This fixture encodes three tolerance values via the complex
AP242 form (MEASURE_REPRESENTATION_ITEM) and provides 0.005 in three places,
while readers that hard-code a single subtype fail.

Byte assertions:
  contains(b'MEASURE_REPRESENTATION_ITEM') or contains(b'LENGTH_MEASURE_WITH_UNIT')
  count(b'0.005') >= 3

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N033",
    defect=(
        "tolerance values encoded via AP242 complex MEASURE_REPRESENTATION_ITEM "
        "form with 0.005 in three places; reader hard-coding plain subtype fails; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
    schema="AP242",
)

# Minimal geometry.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Emit AP242 complex measure form three times with value 0.005.
# The complex entity combines LENGTH_MEASURE_WITH_UNIT + MEASURE_REPRESENTATION_ITEM.
lu_ref = "#9056"  # length unit from add_product_chain
pds_ref = "#9055"  # product definition shape

shape_asp = f._emit_raw(f"SHAPE_ASPECT('datum_surface','',{pds_ref},.T.)")

# Three tolerance values via complex MEASURE_REPRESENTATION_ITEM form.
# Form: (LENGTH_MEASURE_WITH_UNIT() MEASURE_REPRESENTATION_ITEM('') MEASURE_WITH_UNIT(...) REPRESENTATION_ITEM(''))
tol_val1 = f._emit_raw(
    f"(LENGTH_MEASURE_WITH_UNIT()MEASURE_REPRESENTATION_ITEM('')"
    f"MEASURE_WITH_UNIT(LENGTH_MEASURE(0.005),{lu_ref})"
    f"REPRESENTATION_ITEM(''))"
)
tol_val2 = f._emit_raw(
    f"(LENGTH_MEASURE_WITH_UNIT()MEASURE_REPRESENTATION_ITEM('')"
    f"MEASURE_WITH_UNIT(LENGTH_MEASURE(0.005),{lu_ref})"
    f"REPRESENTATION_ITEM(''))"
)
tol_val3 = f._emit_raw(
    f"(LENGTH_MEASURE_WITH_UNIT()MEASURE_REPRESENTATION_ITEM('')"
    f"MEASURE_WITH_UNIT(LENGTH_MEASURE(0.005),{lu_ref})"
    f"REPRESENTATION_ITEM(''))"
)

# Reference the polymorphic values in tolerance entities.
f._emit_raw(
    f"FLATNESS_TOLERANCE('flat1',$,#{tol_val1.eid},#{shape_asp.eid},$)"
)
f._emit_raw(
    f"STRAIGHTNESS_TOLERANCE('str1',$,#{tol_val2.eid},#{shape_asp.eid},$)"
)
f._emit_raw(
    f"CYLINDRICITY_TOLERANCE('cyl1',$,#{tol_val3.eid},#{shape_asp.eid},$)"
)
