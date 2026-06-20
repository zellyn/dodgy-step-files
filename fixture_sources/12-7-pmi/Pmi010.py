"""Pmi010 — Tolerance zone form name from AP242 Ed.2 used in Ed.1 file.

Catalog claim: Several TOLERANCE_ZONE_FORM.name values ('within a sphere',
'within a cone', 'within a single complex surface') were added in AP242 Ed.2.
Used in an Ed.1 file they trigger a WHERE-rule violation.

Reproducer recipe: AP242 Ed.1 file containing TOLERANCE_ZONE_FORM('within a cone').

Byte assertions:
  contains(b'POSITION_TOLERANCE')
  contains(b'TOLERANCE_ZONE_FORM')
  contains(b'DATUM_SYSTEM')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi010",
    defect=(
        "TOLERANCE_ZONE_FORM('within a cone') is an AP242 Ed.2-only name used "
        "in an Ed.1-declared file; triggers WHERE-rule violation on read; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# ── Datum system ───────────────────────────────────────────────────────────────
datum_a = f._emit_raw("DATUM('A','primary datum',#9055,.T.,'A')")
dre = f._emit_raw(f"DATUM_REFERENCE_ELEMENT('',$,#{datum_a.eid})")
drc = f._emit_raw(f"DATUM_REFERENCE_COMPARTMENT('',$,#{dre.eid})")
datum_sys = f._emit_raw(
    f"DATUM_SYSTEM('datum_system_A','',#9055,.T.,(#{drc.eid}))"
)

# ── Tolerance zone with Ed.2-only form name ───────────────────────────────────
shape_asp = f._emit_raw("SHAPE_ASPECT('bore_axis','',#9055,.T.)")
tol_val = f._emit_raw(
    "LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.05),#9056)"
)

# Defect: 'within a cone' is not a valid TOLERANCE_ZONE_FORM name in Ed.1.
tz_form = f._emit_raw("TOLERANCE_ZONE_FORM('within a cone')")

tol_zone = f._emit_raw(
    f"TOLERANCE_ZONE('',#{shape_asp.eid},#{tz_form.eid})"
)

f._emit_raw(
    f"POSITION_TOLERANCE('pos_tol',$,#{tol_val.eid},#{shape_asp.eid},#{datum_sys.eid})"
)
