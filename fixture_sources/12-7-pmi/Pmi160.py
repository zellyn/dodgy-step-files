"""Pmi160 — MMC modifier applied to a FLATNESS (form) tolerance — illegal [DEFECT].

Catalog claim: Material-condition modifiers (Ⓜ MMC / Ⓛ LMC) apply only to
features OF SIZE. A form tolerance such as flatness has no size feature, so a
maximum-material-requirement modifier on it is an ASME Y14.5 rule violation.
This fixture emits a single AP242 complex instance that is simultaneously a
`flatness_tolerance` and a `geometric_tolerance_with_modifiers` bearing
`.MAXIMUM_MATERIAL_REQUIREMENT.`. A compliant reader must warn/reject; silently
accepting it propagates a bad bonus-tolerance calculation. Defect variant of
Pmi159.

Pattern-mined from the NIST MBE-PMI FTC/CTC AP242 test suite (public-domain /
describe-only — pattern only, no bytes copied).

Byte assertions:
  contains(b'FLATNESS_TOLERANCE')
  contains(b'GEOMETRIC_TOLERANCE_WITH_MODIFIERS')
  contains(b'MAXIMUM_MATERIAL_REQUIREMENT')

Tier-3: shape_null == False (GCS+point loads as one vertex, like Pmi010)
Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a  (provisional)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi160",
    schema="AP242",
    defect=(
        "MAXIMUM_MATERIAL_REQUIREMENT modifier on a FLATNESS_TOLERANCE (a form "
        "tolerance with no feature of size) — ASME Y14.5 rule violation; "
        "emitted as a FLATNESS_TOLERANCE + GEOMETRIC_TOLERANCE_WITH_MODIFIERS "
        "complex instance; compliant reader must warn/reject, not accept; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC loads the point as one vertex"
    ),
)

# Minimal geometry wrapped in GCS (single vertex loads; mirrors Pmi010).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain fixed IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

asp = f._emit_raw("SHAPE_ASPECT('flat_face','flat face — no feature of size',#9055,.T.)")
mag = f._emit_raw("LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.02),#9056)")

# DEFECT: MMC modifier on a form (flatness) tolerance — one AP242 complex instance.
f._emit_raw(
    f"(FLATNESS_TOLERANCE()"
    f"GEOMETRIC_TOLERANCE('flat_mmc','ILLEGAL: MMC on flatness (no size feature)',"
    f"#{mag.eid},#{asp.eid})"
    f"GEOMETRIC_TOLERANCE_WITH_MODIFIERS((.MAXIMUM_MATERIAL_REQUIREMENT.)))"
)
