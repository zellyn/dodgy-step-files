"""Pmi157 — CIRCULAR_RUNOUT_TOLERANCE with NO datum reference [DEFECT].

Catalog claim: A runout tolerance is meaningless without a datum axis — ASME
Y14.5 / ISO 1101 require runout to be referenced to a datum. This fixture emits
a `circular_runout_tolerance` with a toleranced feature but NO `datum_system`
(the datum-reference supertype is omitted). A compliant reader must flag the
datum-less runout FCF, not silently accept it. Defect variant of Pmi156.

Pattern-mined from the NIST MBE-PMI FTC/CTC AP242 test suite (public-domain /
describe-only — pattern only, no bytes copied).

Byte assertions:
  contains(b'CIRCULAR_RUNOUT_TOLERANCE')
  not_contains(b'DATUM_SYSTEM')
  not_contains(b'GEOMETRIC_TOLERANCE_WITH_DATUM_REFERENCE')

Tier-3: shape_null == False (GCS+point loads as one vertex, like Pmi010)
Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a  (provisional)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi157",
    schema="AP242",
    defect=(
        "CIRCULAR_RUNOUT_TOLERANCE with no datum-system / datum-reference — "
        "runout requires a datum axis; datum-less runout FCF is GD&T-illegal; "
        "compliant reader must reject/warn, not silently accept; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC loads the point as one vertex"
    ),
)

# Minimal geometry wrapped in GCS (single vertex loads; mirrors Pmi010).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain fixed IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Toleranced cylinder feature + magnitude.
asp = f._emit_raw("SHAPE_ASPECT('cylinder_od','runout feature',#9055,.T.)")
mag = f._emit_raw("LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.05),#9056)")

# DEFECT: runout FCF carries no datum reference at all.
f._emit_raw(
    f"CIRCULAR_RUNOUT_TOLERANCE('circular_runout_no_datum',"
    f"'ILLEGAL: runout requires a datum axis, none supplied',"
    f"#{mag.eid},#{asp.eid})"
)
