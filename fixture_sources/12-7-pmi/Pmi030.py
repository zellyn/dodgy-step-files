"""Pmi030 — Negative projected tolerance zone length.

Catalog claim: projected_zone_definition.magnitude is negative.
Receivers must take the absolute value and warn, or reject; never silently
use the negative value.

Reproducer recipe: projected_zone_definition with magnitude -5.0.

Byte assertions:
  contains(b'PROJECTED_ZONE_DEFINITION')
  contains(b'POSITION_TOLERANCE')
  contains(b'TOLERANCE_ZONE_FORM')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi030",
    schema="AP242",
    defect=(
        "PROJECTED_ZONE_DEFINITION.magnitude is negative (-5.0); receivers must "
        "take the absolute value and warn, or reject outright; silently using the "
        "negative projection length is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Feature to attach the tolerance to.
asp_tol = f._emit_raw("SHAPE_ASPECT('tol_feature','',#9055,.T.)")

# Tolerance value.
tol_val = f._emit_raw("MEASURE_REPRESENTATION_ITEM('tol',LENGTH_MEASURE(0.05),#9056)")

# TOLERANCE_ZONE_FORM gives the zone its shape (cylindrical is typical for position).
zone_form = f._emit_raw("TOLERANCE_ZONE_FORM('cylindrical')")

# Defect: negative magnitude in PROJECTED_ZONE_DEFINITION.
# The magnitude argument is the projection length; -5.0 is illegal.
proj_zone = f._emit_raw(
    f"PROJECTED_ZONE_DEFINITION(LENGTH_MEASURE(-5.0),#{zone_form.eid},$)"
)

# POSITION_TOLERANCE referencing the projected zone definition.
f._emit_raw(
    f"POSITION_TOLERANCE(#{asp_tol.eid},#{tol_val.eid},#{proj_zone.eid},$)"
)
