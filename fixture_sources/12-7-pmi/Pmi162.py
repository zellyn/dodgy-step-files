"""Pmi162 — Full GD&T form/orientation/location symbol set beyond position/perpendicularity/flatness [VALID-BUT-HARD].

Catalog claim: The corpus's semantic-tolerance coverage is limited to position,
perpendicularity, and flatness. AP242 distinguishes six further tolerance
subtypes on their own entity names: `cylindricity_tolerance`,
`roundness_tolerance` (circularity), `straightness_tolerance`,
`angularity_tolerance`, `concentricity_tolerance`, `symmetry_tolerance`. A
reader that maps unknown subtypes onto a generic tolerance loses the symbol
semantics (and, for the datum-referenced ones, the datum link).

Pattern-mined from the NIST MBE-PMI FTC/CTC AP242 test suite (public-domain /
describe-only — pattern only, no bytes copied).

Byte assertions:
  contains(b'CYLINDRICITY_TOLERANCE')
  contains(b'ROUNDNESS_TOLERANCE')
  contains(b'STRAIGHTNESS_TOLERANCE')
  contains(b'ANGULARITY_TOLERANCE')
  contains(b'CONCENTRICITY_TOLERANCE')
  contains(b'SYMMETRY_TOLERANCE')

Tier-3: shape_null == False (GCS+point loads as one vertex, like Pmi010)
Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a  (provisional)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi162",
    schema="AP242",
    defect=(
        "Six additional AP242 tolerance subtypes each on its own entity name: "
        "CYLINDRICITY_TOLERANCE, ROUNDNESS_TOLERANCE (circularity), "
        "STRAIGHTNESS_TOLERANCE (form; no datum), plus datum-referenced "
        "ANGULARITY_TOLERANCE, CONCENTRICITY_TOLERANCE, SYMMETRY_TOLERANCE; "
        "generic-tolerance mapping loses the symbol semantics; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC loads the point as one vertex"
    ),
)

# Minimal geometry wrapped in GCS (single vertex loads; mirrors Pmi010).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain fixed IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# ── Datum system A for the datum-referenced tolerances ───────────────────────
datum_a = f._emit_raw("DATUM('A','primary datum',#9055,.T.,'A')")
dre = f._emit_raw(f"DATUM_REFERENCE_ELEMENT('',$,#{datum_a.eid})")
drc = f._emit_raw(f"DATUM_REFERENCE_COMPARTMENT('',$,#{dre.eid})")
datum_sys = f._emit_raw(
    f"DATUM_SYSTEM('datum_system_A','',#9055,.T.,(#{drc.eid}))"
)

# ── Feature aspects ──────────────────────────────────────────────────────────
asp_cyl = f._emit_raw("SHAPE_ASPECT('cylinder','cylindrical feature',#9055,.T.)")
asp_face = f._emit_raw("SHAPE_ASPECT('angled_face','angled planar feature',#9055,.T.)")
asp_slot = f._emit_raw("SHAPE_ASPECT('slot','slot median feature',#9055,.T.)")

mag = f._emit_raw("LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.05),#9056)")

# ── Form tolerances (no datum) ───────────────────────────────────────────────
f._emit_raw(
    f"CYLINDRICITY_TOLERANCE('cylindricity','0.05 cylindricity',#{mag.eid},#{asp_cyl.eid})"
)
f._emit_raw(
    f"ROUNDNESS_TOLERANCE('circularity','0.05 circularity',#{mag.eid},#{asp_cyl.eid})"
)
f._emit_raw(
    f"STRAIGHTNESS_TOLERANCE('straightness','0.05 straightness',#{mag.eid},#{asp_cyl.eid})"
)

# ── Orientation / location tolerances (datum-referenced) ─────────────────────
f._emit_raw(
    f"ANGULARITY_TOLERANCE('angularity','0.05 angularity wrt A',"
    f"#{mag.eid},#{asp_face.eid},#{datum_sys.eid})"
)
f._emit_raw(
    f"CONCENTRICITY_TOLERANCE('concentricity','0.05 concentricity wrt A',"
    f"#{mag.eid},#{asp_cyl.eid},#{datum_sys.eid})"
)
f._emit_raw(
    f"SYMMETRY_TOLERANCE('symmetry','0.05 symmetry wrt A',"
    f"#{mag.eid},#{asp_slot.eid},#{datum_sys.eid})"
)
