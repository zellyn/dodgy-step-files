"""N032 — Tolerance type entity coverage: AP242 tolerance entities dropped on import.

STEP file uses AP242 tolerance entities (RUNOUT_TOLERANCE_WITH_VALUES,
RUNOUT_ZONE_DEFINITION, RUNOUT_ZONE_ORIENTATION_REFERENCE_DIRECTION) that an
AP214-only importer drops because they aren't in its parser. Repeated HOOPS
Exchange fixes prove this class is large and ongoing.

Byte assertions:
  contains(b'RUNOUT_TOLERANCE_WITH_VALUES')
  contains(b'RUNOUT_ZONE_DEFINITION')
  contains(b'RUNOUT_ZONE_ORIENTATION_REFERENCE_DIRECTION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N032",
    defect=(
        "AP242 RUNOUT_TOLERANCE_WITH_VALUES + RUNOUT_ZONE_DEFINITION + "
        "RUNOUT_ZONE_ORIENTATION_REFERENCE_DIRECTION; AP214-only importer drops "
        "all; GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
    schema="AP242",
)

# Minimal geometry in GEOMETRIC_CURVE_SET so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Reference IDs from add_product_chain for PRODUCT_DEFINITION_SHAPE and length unit.
# Use the known pattern from Pmi010: #9055 = PRODUCT_DEFINITION_SHAPE, #9056 = length unit.
# Actually emit them fresh here.
pds_eid = None  # will use raw numbering after chain
# After add_product_chain, PRODUCT_DEFINITION_SHAPE and length unit are the last two
# significant entities.  We can reference them by searching forward, but simpler
# to emit a fresh shape_aspect root.
shape_asp = f._emit_raw("SHAPE_ASPECT('cylindrical_surface','',#9055,.T.)")

# Tolerance value: 0.05 mm total runout
tol_val = f._emit_raw(
    "LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.05),#9056)"
)

# Datum for reference
datum_a = f._emit_raw("DATUM('A','primary_datum',#9055,.T.,'A')")
dre = f._emit_raw(f"DATUM_REFERENCE_ELEMENT('',$,#{datum_a.eid})")
drc = f._emit_raw(f"DATUM_REFERENCE_COMPARTMENT('',$,#{dre.eid})")
datum_sys = f._emit_raw(
    f"DATUM_SYSTEM('ds_A','',#9055,.T.,(#{drc.eid}))"
)

# RUNOUT_ZONE_ORIENTATION_REFERENCE_DIRECTION — AP242-specific
runout_dir = f._emit_raw(
    f"RUNOUT_ZONE_ORIENTATION_REFERENCE_DIRECTION(#{datum_sys.eid})"
)

# RUNOUT_ZONE_DEFINITION — AP242-specific
runout_zone_def = f._emit_raw(
    f"RUNOUT_ZONE_DEFINITION('',#{shape_asp.eid},#{runout_dir.eid})"
)

# RUNOUT_TOLERANCE_WITH_VALUES — AP242-specific
f._emit_raw(
    f"RUNOUT_TOLERANCE_WITH_VALUES('runout_tol','total_runout',"
    f"#{tol_val.eid},#{shape_asp.eid},#{datum_sys.eid})"
)
